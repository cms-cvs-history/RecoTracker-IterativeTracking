import FWCore.ParameterSet.Config as cms

import RecoLocalTracker.SiPixelRecHits.SiPixelRecHits_cfi
#TRACKER HITS
thPixelRecHits = RecoLocalTracker.SiPixelRecHits.SiPixelRecHits_cfi.siPixelRecHits.clone()
import RecoLocalTracker.SiStripRecHitConverter.SiStripRecHitConverter_cfi
thStripRecHits = RecoLocalTracker.SiStripRecHitConverter.SiStripRecHitConverter_cfi.siStripMatchedRecHits.clone()
thPixelRecHits.src = 'thClusters'
thStripRecHits.ClusterProducer = 'thClusters'



import RecoTracker.TkSeedGenerator.GlobalMixedSeeds_cfi
#SEEDS
thPLSeeds = RecoTracker.TkSeedGenerator.GlobalMixedSeeds_cfi.globalMixedSeeds.clone()
import RecoTracker.MeasurementDet.MeasurementTrackerESProducer_cfi
thPLSeeds.OrderedHitsFactoryPSet.SeedingLayers = 'ThLayerPairs'
thPLSeeds.RegionFactoryPSet.RegionPSet.ptMin = 0.6
thPLSeeds.RegionFactoryPSet.RegionPSet.originHalfLength = 7.0
thPLSeeds.RegionFactoryPSet.RegionPSet.originRadius = 0.7

#TRAJECTORY MEASUREMENT
thMeasurementTracker = RecoTracker.MeasurementDet.MeasurementTrackerESProducer_cfi.MeasurementTracker.clone()
import TrackingTools.TrajectoryFiltering.TrajectoryFilterESProducer_cfi
thMeasurementTracker.ComponentName = 'thMeasurementTracker'
thMeasurementTracker.pixelClusterProducer = 'thClusters'
thMeasurementTracker.stripClusterProducer = 'thClusters'

#TRAJECTORY FILTER
thCkfTrajectoryFilter = TrackingTools.TrajectoryFiltering.TrajectoryFilterESProducer_cfi.trajectoryFilterESProducer.clone()
import RecoTracker.CkfPattern.GroupedCkfTrajectoryBuilderESProducer_cfi
thCkfTrajectoryFilter.ComponentName = 'thCkfTrajectoryFilter'
thCkfTrajectoryFilter.filterPset.maxLostHits = 0
thCkfTrajectoryFilter.filterPset.minimumNumberOfHits = 3
thCkfTrajectoryFilter.filterPset.minPt = 0.3

#TRAJECTORY BUILDER
thCkfTrajectoryBuilder = RecoTracker.CkfPattern.GroupedCkfTrajectoryBuilderESProducer_cfi.GroupedCkfTrajectoryBuilder.clone()
import RecoTracker.CkfPattern.CkfTrackCandidates_cfi
thCkfTrajectoryBuilder.ComponentName = 'thCkfTrajectoryBuilder'
thCkfTrajectoryBuilder.MeasurementTrackerName = 'thMeasurementTracker'
thCkfTrajectoryBuilder.trajectoryFilterName = 'thCkfTrajectoryFilter'


#TRACK CANDIDATES
thTrackCandidates = RecoTracker.CkfPattern.CkfTrackCandidates_cfi.ckfTrackCandidates.clone()
import RecoTracker.TrackProducer.CTFFinalFitWithMaterial_cfi
thTrackCandidates.src = cms.InputTag('thPLSeeds')
thTrackCandidates.TrajectoryBuilder = 'thCkfTrajectoryBuilder'
thTrackCandidates.doSeedingRegionRebuilding = True
thTrackCandidates.useHitsSplitting = True


#TRACKS
thWithMaterialTracks = RecoTracker.TrackProducer.CTFFinalFitWithMaterial_cfi.ctfWithMaterialTracks.clone()
thWithMaterialTracks.AlgorithmName = cms.string('iter3')
thWithMaterialTracks.src = 'thTrackCandidates'
thWithMaterialTracks.clusterRemovalInfo = 'thClusters'



#HIT REMOVAL
thClusters = cms.EDFilter("TrackClusterRemover",
    oldClusterRemovalInfo = cms.InputTag("secClusters"),
    trajectories = cms.InputTag("secStep"),
    pixelClusters = cms.InputTag("secClusters"),
    Common = cms.PSet(
        maxChi2 = cms.double(30.0)
    ),
    stripClusters = cms.InputTag("secClusters")
)

#SEEDING LAYERS
thlayerpairs = cms.ESProducer("MixedLayerPairsESProducer",
    ComponentName = cms.string('ThLayerPairs'),
    layerList = cms.vstring('BPix1+BPix2', 
        'BPix2+BPix3',
        'BPix1+FPix1_pos',
        'BPix1+FPix1_neg',
        'FPix1_pos+FPix2_pos',
        'FPix1_neg+FPix2_neg',
        'FPix2_pos+TEC2_pos',
        'FPix2_neg+TEC2_neg'),
    TEC = cms.PSet(
        matchedRecHits = cms.InputTag("thStripRecHits","matchedRecHit"),
        useRingSlector = cms.untracked.bool(True),
        TTRHBuilder = cms.string('WithTrackAngle'),
        minRing = cms.int32(1),
        maxRing = cms.int32(2)
    ),
    BPix = cms.PSet(
        useErrorsFromParam = cms.untracked.bool(True),
        hitErrorRPhi = cms.double(0.0027),
        TTRHBuilder = cms.string('TTRHBuilderWithoutAngle4MixedPairs'),
        HitProducer = cms.string('thPixelRecHits'),
        hitErrorRZ = cms.double(0.006)
    ),
    FPix = cms.PSet(
        useErrorsFromParam = cms.untracked.bool(True),
        hitErrorRPhi = cms.double(0.0051),
        TTRHBuilder = cms.string('TTRHBuilderWithoutAngle4MixedPairs'),
        HitProducer = cms.string('thPixelRecHits'),
        hitErrorRZ = cms.double(0.0036)
    )
)

import RecoTracker.FinalTrackSelectors.selectHighPurity_cfi
thStepVtx = RecoTracker.FinalTrackSelectors.selectHighPurity_cfi.selectHighPurity.clone()
thStepVtx.src = 'thWithMaterialTracks'
thStepVtx.copyTrajectories = True
thStepVtx.chi2n_par = 0.9
thStepVtx.res_par = ( 0.003, 0.001 )
thStepVtx.d0_par1 = ( 0.9, 3.0 )
thStepVtx.dz_par1 = ( 0.9, 3.0 )
thStepVtx.d0_par2 = ( 1.0, 3.0 )
thStepVtx.dz_par2 = ( 1.0, 3.0 )

thStepTrk = RecoTracker.FinalTrackSelectors.selectHighPurity_cfi.selectHighPurity.clone()
thStepTrk.src = 'thWithMaterialTracks'
thStepTrk.copyTrajectories = True
thStepTrk.chi2n_par = 0.5
thStepTrk.res_par = ( 0.003, 0.001 )
thStepTrk.minNumberLayers = 5
thStepTrk.d0_par1 = ( 1.0, 4.0 )
thStepTrk.dz_par1 = ( 1.0, 4.0 )
thStepTrk.d0_par2 = ( 1.0, 4.0 )
thStepTrk.dz_par2 = ( 1.0, 4.0 )
import RecoTracker.FinalTrackSelectors.ctfrsTrackListMerger_cfi

thStep = RecoTracker.FinalTrackSelectors.ctfrsTrackListMerger_cfi.ctfrsTrackListMerger.clone()
thStep.TrackProducer1 = 'thStepVtx'
thStep.TrackProducer2 = 'thStepTrk'

thirdStep = cms.Sequence(thClusters*
                         thPixelRecHits*thStripRecHits*
                         thPLSeeds*
                         thTrackCandidates*
                         thWithMaterialTracks*
                         thStepVtx*
                         thStepTrk*
                         thStep)
