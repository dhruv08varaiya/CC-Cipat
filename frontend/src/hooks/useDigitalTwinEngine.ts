import { useState, useEffect, useRef, useCallback } from 'react';

export interface LiveTransaction {
  id: string;
  timestamp: string;
  serviceType: string;
  amount?: number;
  classification: 'RESTRICTED' | 'CONFIDENTIAL' | 'INTERNAL' | 'PUBLIC';
  targetTier: 'PRIVATE' | 'PUBLIC';
  status: 'COMPLETED' | 'BLOCKED' | 'QUEUED' | 'DROPPED';
  latencyMs: number;
  breakdown: {
    network: number;
    security: number;
    queue: number;
    service: number;
    db: number;
  };
}

export interface MetricSnapshot {
  timeSec: number;
  rps: number;
  latencyMs: number;
  p95LatencyMs: number;
  privateQueue: number;
  publicQueue: number;
  totalQueue: number;
  privateUtilPct: number;
  publicUtilPct: number;
  activePublicInstances: number;
  autoscalerState: 'IDLE' | 'SCALE_OUT' | 'COOLDOWN' | 'SCALE_IN';
  droppedRequests: number;
}

export interface DigitalTwinConfig {
  targetRps: number;
  preset: string;
  chaosCoreDrop: boolean;
  chaosNetworkSpike: boolean;
  chaosDbLock: boolean;
  chaosAttackProbe: boolean;
  playbackSpeed: number; // 0.5x, 1x, 2x, 5x
  isPaused: boolean;
}

const SERVICE_CATALOG = [
  { type: 'fund_transfer', class: 'RESTRICTED' as const, target: 'PRIVATE' as const, baseMs: 14, db: true },
  { type: 'kyc_verification', class: 'RESTRICTED' as const, target: 'PRIVATE' as const, baseMs: 22, db: true },
  { type: 'loan_evaluation', class: 'CONFIDENTIAL' as const, target: 'PRIVATE' as const, baseMs: 18, db: true },
  { type: 'balance_inquiry', class: 'CONFIDENTIAL' as const, target: 'PRIVATE' as const, baseMs: 8, db: true },
  { type: 'fx_rate_lookup', class: 'PUBLIC' as const, target: 'PUBLIC' as const, baseMs: 6, db: false },
  { type: 'branch_atm_locator', class: 'PUBLIC' as const, target: 'PUBLIC' as const, baseMs: 5, db: false },
  { type: 'interest_calculator', class: 'INTERNAL' as const, target: 'PUBLIC' as const, baseMs: 9, db: false },
  { type: 'support_faq_search', class: 'PUBLIC' as const, target: 'PUBLIC' as const, baseMs: 7, db: false },
];

export const useDigitalTwinEngine = () => {
  // Config state
  const [config, setConfig] = useState<DigitalTwinConfig>({
    targetRps: 600,
    preset: 'normal',
    chaosCoreDrop: false,
    chaosNetworkSpike: false,
    chaosDbLock: false,
    chaosAttackProbe: false,
    playbackSpeed: 1,
    isPaused: false,
  });

  // Current real-time metrics
  const [currentMetrics, setCurrentMetrics] = useState<MetricSnapshot>({
    timeSec: 0,
    rps: 600,
    latencyMs: 22.4,
    p95LatencyMs: 29.8,
    privateQueue: 0,
    publicQueue: 0,
    totalQueue: 0,
    privateUtilPct: 24.5,
    publicUtilPct: 18.2,
    activePublicInstances: 2,
    autoscalerState: 'IDLE',
    droppedRequests: 0,
  });

  // Rolling Ring Buffers (Fixed length = 60 points)
  const [history, setHistory] = useState<MetricSnapshot[]>(() => {
    const initial: MetricSnapshot[] = [];
    for (let i = 60; i >= 0; i--) {
      initial.push({
        timeSec: -i * 0.5,
        rps: 600,
        latencyMs: 22.4,
        p95LatencyMs: 29.8,
        privateQueue: 0,
        publicQueue: 0,
        totalQueue: 0,
        privateUtilPct: 24.5,
        publicUtilPct: 18.2,
        activePublicInstances: 2,
        autoscalerState: 'IDLE',
        droppedRequests: 0,
      });
    }
    return initial;
  });

  // Live transaction ledger stream (10 rows)
  const [recentTransactions, setRecentTransactions] = useState<LiveTransaction[]>([]);

  // Total accumulators
  const [totalProcessed, setTotalProcessed] = useState(0);
  const [totalDropped, setTotalDropped] = useState(0);

  // Internal mutable simulation state refs (Zero React overhead during 60Hz ticks)
  const stateRef = useRef({
    timeSec: 0,
    activeInstances: 2,
    provisioningTimer: 0,
    scaleCooldown: 0,
    autoscalerState: 'IDLE' as MetricSnapshot['autoscalerState'],
    consecutiveHighUtil: 0,
    consecutiveLowUtil: 0,
    privateQueue: 0,
    publicQueue: 0,
    lastTickTime: performance.now(),
    txnCounter: 1000,
    droppedCount: 0,
    processedCount: 0,
  });

  const configRef = useRef(config);
  configRef.current = config;

  // Change preset helper
  const applyPreset = useCallback((presetId: string) => {
    switch (presetId) {
      case 'normal':
        setConfig(prev => ({ ...prev, targetRps: 600, preset: 'normal', chaosCoreDrop: false, chaosNetworkSpike: false, chaosDbLock: false, chaosAttackProbe: false }));
        break;
      case 'salary_rush':
        setConfig(prev => ({ ...prev, targetRps: 1800, preset: 'salary_rush', chaosCoreDrop: false, chaosNetworkSpike: false, chaosDbLock: false, chaosAttackProbe: false }));
        break;
      case 'flash_burst':
        setConfig(prev => ({ ...prev, targetRps: 2800, preset: 'flash_burst', chaosCoreDrop: false, chaosNetworkSpike: false, chaosDbLock: false, chaosAttackProbe: false }));
        break;
      case 'chaos_blackout':
        setConfig(prev => ({ ...prev, targetRps: 1400, preset: 'chaos_blackout', chaosCoreDrop: true, chaosNetworkSpike: false, chaosDbLock: false, chaosAttackProbe: false }));
        break;
      case 'sqli_attack':
        setConfig(prev => ({ ...prev, targetRps: 1200, preset: 'sqli_attack', chaosCoreDrop: false, chaosNetworkSpike: false, chaosDbLock: false, chaosAttackProbe: true }));
        break;
      default:
        break;
    }
  }, []);

  // Main simulation tick loop (Runs every 100ms for smooth UI updates without battery drain)
  useEffect(() => {
    let animFrame: number;
    let lastUpdate = performance.now();

    const tick = (now: number) => {
      const elapsed = (now - lastUpdate) / 1000;
      
      if (elapsed >= 0.1) { // 100ms update interval (10 updates/sec with smooth transitions)
        lastUpdate = now;
        const currentCfg = configRef.current;
        const s = stateRef.current;

        if (!currentCfg.isPaused) {
          const speed = currentCfg.playbackSpeed;
          const dt = elapsed * speed;
          s.timeSec += dt;

          const rps = currentCfg.targetRps;
          const privateCoresAvailable = currentCfg.chaosCoreDrop ? 24 : 48; // 50% drop if chaos
          const dbCapacity = currentCfg.chaosDbLock ? 12 : 64; // Constrained if locked
          const networkSpikeMs = currentCfg.chaosNetworkSpike ? 25.0 : 0.0;

          // Compute traffic distribution
          const privateRps = rps * 0.70; // 70% private tier traffic
          const publicRps = rps * 0.30; // 30% public tier traffic

          // Private DC utilization & M/G/c queue
          // Capacity per core ~ 25 RPS
          const privateMaxCapacity = privateCoresAvailable * 25;
          const privateUtilRaw = (privateRps / privateMaxCapacity) * 100;
          const privateUtilPct = Math.min(100, Math.max(8, privateUtilRaw + (Math.sin(s.timeSec * 2) * 3)));
          
          if (privateUtilPct > 90) {
            s.privateQueue = Math.min(250, s.privateQueue + Math.floor((privateUtilPct - 88) * 0.4));
          } else {
            s.privateQueue = Math.max(0, s.privateQueue - 4);
          }

          // Public Cloud Capacity (4 cores per instance, ~35 RPS per core = 140 RPS per inst)
          const publicInst = s.activeInstances;
          const publicMaxCapacity = publicInst * 140;
          const publicUtilRaw = (publicRps / publicMaxCapacity) * 100;
          const publicUtilPct = Math.min(100, Math.max(6, publicUtilRaw + (Math.cos(s.timeSec * 1.5) * 4)));

          if (publicUtilPct > 85) {
            s.publicQueue = Math.min(180, s.publicQueue + Math.floor((publicUtilPct - 82) * 0.3));
          } else {
            s.publicQueue = Math.max(0, s.publicQueue - 5);
          }

          // Autoscaler State Machine
          if (s.scaleCooldown > 0) {
            s.scaleCooldown -= dt;
            s.autoscalerState = 'COOLDOWN';
          } else if (s.provisioningTimer > 0) {
            s.provisioningTimer -= dt;
            s.autoscalerState = 'SCALE_OUT';
            if (s.provisioningTimer <= 0) {
              s.activeInstances = Math.min(20, s.activeInstances + 2);
              s.scaleCooldown = 2.0; // 2s cooldown
            }
          } else {
            if (publicUtilPct > 70 && s.activeInstances < 20) {
              s.consecutiveHighUtil += dt;
              if (s.consecutiveHighUtil >= 0.6) {
                s.provisioningTimer = 0.8; // 800ms provisioning delay
                s.autoscalerState = 'SCALE_OUT';
                s.consecutiveHighUtil = 0;
              }
            } else if (publicUtilPct < 35 && s.activeInstances > 2) {
              s.consecutiveLowUtil += dt;
              if (s.consecutiveLowUtil >= 1.5) {
                s.activeInstances = Math.max(2, s.activeInstances - 2);
                s.autoscalerState = 'SCALE_IN';
                s.scaleCooldown = 1.5;
                s.consecutiveLowUtil = 0;
              }
            } else {
              s.autoscalerState = 'IDLE';
              s.consecutiveHighUtil = 0;
              s.consecutiveLowUtil = 0;
            }
          }

          // Compute realistic response times
          const baseLatency = 14.5 + networkSpikeMs;
          const queueDelayMs = (s.privateQueue * 0.15) + (s.publicQueue * 0.10);
          const dbDelayMs = currentCfg.chaosDbLock ? 18.5 : 2.5;
          const avgLatency = parseFloat((baseLatency + queueDelayMs + dbDelayMs + (Math.random() * 2.5)).toFixed(2));
          const p95Latency = parseFloat((avgLatency * 1.35 + (Math.random() * 3.0)).toFixed(2));

          // Dropped requests if saturated
          let newDrops = 0;
          if (s.privateQueue > 150 || s.publicQueue > 120) {
            newDrops = Math.floor(Math.random() * 3) + 1;
            s.droppedCount += newDrops;
          }

          const processedInInterval = Math.round(rps * elapsed);
          s.processedCount += processedInInterval;

          const newSnapshot: MetricSnapshot = {
            timeSec: parseFloat(s.timeSec.toFixed(1)),
            rps: rps + Math.floor((Math.random() - 0.5) * (rps * 0.05)),
            latencyMs: avgLatency,
            p95LatencyMs: p95Latency,
            privateQueue: s.privateQueue,
            publicQueue: s.publicQueue,
            totalQueue: s.privateQueue + s.publicQueue,
            privateUtilPct: parseFloat(privateUtilPct.toFixed(1)),
            publicUtilPct: parseFloat(publicUtilPct.toFixed(1)),
            activePublicInstances: s.activeInstances,
            autoscalerState: s.autoscalerState,
            droppedRequests: s.droppedCount,
          };

          setCurrentMetrics(newSnapshot);
          setTotalProcessed(s.processedCount);
          setTotalDropped(s.droppedCount);

          // Update rolling ring buffer (max 60 points)
          setHistory(prev => [...prev.slice(1), newSnapshot]);

          // Generate simulated real-time transaction event (every tick generates 1-2 new transactions)
          const svc = SERVICE_CATALOG[Math.floor(Math.random() * SERVICE_CATALOG.length)];
          s.txnCounter += 1;
          const isBlocked = currentCfg.chaosAttackProbe && (svc.type === 'fund_transfer' || Math.random() < 0.4);

          const netMs = parseFloat((3.0 + networkSpikeMs + Math.random() * 1.5).toFixed(1));
          const secMs = parseFloat((2.5 + Math.random() * 1.0).toFixed(1));
          const qMs = parseFloat((svc.target === 'PRIVATE' ? s.privateQueue * 0.12 : s.publicQueue * 0.08).toFixed(1));
          const servMs = parseFloat((svc.baseMs + Math.random() * 3.0).toFixed(1));
          const dbMs = svc.db ? (currentCfg.chaosDbLock ? 16.0 : 4.2) : 0.0;
          const totalMs = parseFloat((netMs + secMs + qMs + servMs + dbMs).toFixed(1));

          const newTxn: LiveTransaction = {
            id: `TXN_${s.txnCounter}`,
            timestamp: new Date().toLocaleTimeString(),
            serviceType: isBlocked ? 'malicious_sql_injection_probe' : svc.type,
            amount: svc.type === 'fund_transfer' ? parseFloat((Math.random() * 12000 + 50).toFixed(2)) : undefined,
            classification: isBlocked ? 'RESTRICTED' : svc.class,
            targetTier: isBlocked ? 'PRIVATE' : svc.target,
            status: isBlocked ? 'BLOCKED' : (newDrops > 0 ? 'DROPPED' : 'COMPLETED'),
            latencyMs: isBlocked ? 3.2 : totalMs,
            breakdown: {
              network: netMs,
              security: secMs,
              queue: qMs,
              service: servMs,
              db: dbMs
            }
          };

          setRecentTransactions(prev => [newTxn, ...prev.slice(0, 9)]);
        }
      }

      animFrame = requestAnimationFrame(tick);
    };

    animFrame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animFrame);
  }, []);

  return {
    config,
    setConfig,
    applyPreset,
    currentMetrics,
    history,
    recentTransactions,
    totalProcessed,
    totalDropped,
  };
};
