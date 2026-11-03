"""Historical review-only generator. Product V1 parameters supersede this draft."""
from pathlib import Path
from decimal import Decimal as D, ROUND_HALF_UP
import json

ROOT = Path(__file__).resolve().parent
PRICING = ROOT.parent / '2026-11-01-vehicle-economy/pricing-candidate.json'
GROWTH = ROOT.parent / '2026-11-01-vehicle-growth/candidate.json'
prices = json.loads(PRICING.read_text())
growth = json.loads(GROWTH.read_text())


def rnd(value):
    return int(D(value).quantize(D(1), rounding=ROUND_HALF_UP))


candidate = {
    'id': 'product-master-review-20261102-v2',
    'status': 'historical-review-config-superseded-by-product-v1-not-for-implementation',
    'supersededBy': '../2026-11-02-product-v1/parameters.json',
    'revisionDate': '2026-11-02',
    'confirmed': {
        'mapNpcAdditions': [2, 4, 6, 8, 10], 'maxNpcCount': 30,
        'maxTeamIncludingProtagonist': 31, 'baseFeeYuan': 10,
        'maxSimultaneousPlayerOrders': None, 'vehicleMaxLevel': 30,
        'orderSelection': {'fixedOrderCountCap': False, 'capacityCheck': 'sum-selected-batch-weight-not-above-actual-vehicle-capacity',
                           'addOrdersMidTrip': False, 'nextBatchAfterAllCurrentOrdersCompleted': True},
        'routeSelection': 'system-offers-fast-balanced-smooth-and-arranges-pickup-delivery-order-player-selects-one',
        'npcIncome': {'limited': True, 'idleIncomeHasCap': True, 'purpose': 'encourage-return-and-active-play',
                      'capAmountPeriodAndRecovery': 'not-yet-decided'},
        'stageProgression': {'earlyRisk': 'low', 'riskIncreasesWithProgress': True,
                             'earlySupplies': ['purified-water', 'instant-noodles'],
                             'laterSupplies': ['drinks', 'milk-tea', 'fast-food', 'premium-meals'],
                             'supplySpendingIncreasesWithProgress': True,
                             'retainCheapOptionsOrForceReplacement': 'not-yet-decided'},
        'investmentBalanceCorrection': 'later-user-triggered-stage-testing-not-verified-now',
        'supplyAccess': 'anywhere-button-no-shop-detour',
        'zeroEnergy': {'movement': 'stop-at-current-location',
                       'recovery': ['paid-food-or-drink', 'free-rest-if-no-money'],
                       'freeRestTakesLongerThanPaidSupply': True,
                       'recoveryTimeMayCauseOrderLateness': True,
                       'resume': 'same-location-current-batch',
                       'exactRecoveryAmountsAndDurations': 'not-yet-decided'},
        'deliverySettlementPresentation': {'perOrderIncome': 'immediate-on-delivery-once',
                                           'perOrderFeedback': ['income', 'on-time-or-late', 'food-condition', 'customer-feedback'],
                                           'perOrderConfirmationRequired': False,
                                           'briefFeedbackAddsBlockingPause': False,
                                           'fullSummaryWhen': 'all-orders-in-batch-delivered',
                                           'summaryFields': ['delivery-income', 'actual-supply-expenses', 'net-delivery-income', 'experience'],
                                           'summaryGrantsRewardsAgain': False,
                                           'cancelledPartialBatchSummary': 'return-home-retain-completed-results-and-real-expenses-not-all-delivered'},
        'deliveryCancellation': {'scope': 'all-unfinished-orders-in-current-batch', 'endsBatch': True,
                                 'returnTo': 'home', 'preserveCurrentRoadPosition': True,
                                 'retainCompletedOrderIncomeAndExperience': True, 'unfinishedOrderRewards': False,
                                 'extraMoneyOrReputationPenalty': False, 'refundConsumedSupplies': False,
                                 'cancelledOrdersCountAsCompleted': False, 'allowNewBatchAfterCancellation': True,
                                 'closingAppMeansCancellation': False},
        'display': 'round half up to integers; preserve actual calculation precision',
        'progressionGuidance': {'affordabilityPromptsGoToRelevantPage': True,
                                'rewardOnlyAfterSuccessfulPurchaseRecruitmentOrUnlock': True,
                                'rewardKinds': ['coins', 'supplies'],
                                'mapUnlockRequiresFeeAndOperatingProgress': True},
        'mapUnlock': {'paymentRequired': True, 'operatingProgressRequired': True,
                      'exactFeeAndConditionCombination': 'pm-candidate-for-unified-review'},
        'npcJobs': 'automatic acceptance and delivery; player recruits, assigns vehicles and upgrades',
        'visualDirection': {'decisionDate': '2026-11-02', 'layoutAndInformation': 'concept B', 'mapRendering': 'concept C', 'fusionPreviewNeedsReview': True},
    },
    'proposed': {
        'progressionTasks': {'candidate': '../2026-11-02-progression-tasks/candidate.json',
                             'detailsStatus': 'pm-recommended-not-approved'},
        'energy': {'supplyValueScope': 'old-low-cost-reference-not-all-stages-current-staged-values-need-design',
                   'max': 100, 'roadPerKm': 2, 'perPickupService': 1, 'perDelivery': 1,
                   'water': {'priceYuan': 1, 'restore': 20, 'realSeconds': 1, 'gameSeconds': 30},
                   'meal': {'priceYuan': 3, 'restore': 70, 'realSeconds': 3, 'gameSeconds': 120},
                   'idleRest': {'priceYuan': 0, 'realSeconds': 20, 'restoreTo': 100},
                   'activeRest': {'priceYuan': 0, 'realSeconds': 10, 'gameSeconds': 600, 'restore': 20}},
        'timing': {'roadGameSecondsPerRealSecond': 40, 'ordinarySlackGameSeconds': 300,
                   'urgentSlackGameSeconds': 180, 'planningReadingReceiptsPauseTripClock': True,
                   'clickingOnlyShortensRealWait': True},
        'weather': {'status': 'old-pm-numeric-reference-stage-curve-not-approved',
                    'rainProbabilityPercentByMap': [15, 20, 25, 30, 35],
                    'severeProbabilityPercentByMap': [0, 2, 3, 5, 8],
                    'rainRoadTimeExtraPercent': 10, 'severeRoadTimeExtraPercent': 25,
                    'midTripChangeProbabilityPercent': 5, 'maxMidTripChanges': 1},
        'redLights': {'probabilityPercentByMap': [15, 20, 25, 30, 35],
                      'maxEventsPerTrip': 2, 'maxTotalDelayGameSeconds': 180},
        'damage': {'status': 'old-pm-numeric-reference-stage-scaling-needs-design',
                   'routeOrder': ['fast', 'balanced', 'smooth'],
                   'fragileProbabilitiesPercent': [12, 6, 2],
                   'normalProbabilitiesPercent': [6, 3, 1],
                   'durableProbabilitiesPercent': [2, 1, 0],
                   'rainExtraPercentagePoints': 2, 'severeExtraPercentagePoints': 5,
                   'probabilityCapPercent': 25, 'oneFinalOutcomePerOrder': True,
                   'severityProbabilityPercent': [70, 25, 5],
                   'incomeRetentionPercent': [90, 75, 50]},
        'lateness': {'onTimeRetentionPercent': 100,
                     'bands': [{'aboveGameSecondsLate': 0, 'upToGameSecondsLate': 300, 'retainPercent': 95, 'reputationDelta': -1},
                               {'aboveGameSecondsLate': 300, 'upToGameSecondsLate': 600, 'retainPercent': 85, 'reputationDelta': -3},
                               {'aboveGameSecondsLate': 600, 'upToGameSecondsLate': None, 'retainPercent': 75, 'reputationDelta': -5}],
                     'canCompleteAfterDeadline': True, 'reputationDoesNotMultiplySameOrderIncomeAgain': True},
        'npcTraining': {'maxLevel': 30, 'incomeBonusAtMaxPercent': 20,
                        'fixedWorkTimeReductionAtMaxPercent': 15,
                        'growthProgress': 'same G(L) as vehicle-growth candidate',
                        'fixedCostReferenceYuan': 1800,
                        'cumulativeCost': 'roundHalfUp(1800*L*(L-1)/435) whole yuan',
                        'independentOfHiringOrdinalAndAssignedVehicle': True},
        'npcRest': {'referenceCycleIncludesRoutineRest': True, 'separateFoodChargesInFirstPass': False},
        'offline': {'status': 'old-proposal-superseded-as-default-by-user-idle-income-cap-decision',
                    'historicalOnly': {'maxRealHours': 8, 'normalIncomeRetentionPercent': 70, 'noPlayerDailyActiveRevenueGate': True},
                    'oneTeamOneNonOverlappingTimeInterval': True},
        'npcIncomeCap': {'status': 'direction-confirmed-details-open', 'amountYuan': None, 'period': None,
                         'recoveryCondition': None, 'sharedWithOnlineAutoIncome': None,
                         'doNotAssumeOpeningAppResetsCap': True, 'doNotSilentlyRestoreHistorical500OrderCap': True},
        'mapEntry': [{'map': 2, 'teamLifetimeCompletedOrders': 60, 'npcOwned': 1, 'ownedVehicleTierAtLeast': 'C', 'vehicleLevelAtLeast': 5, 'unlockFeeYuanCandidate': 500},
                     {'map': 3, 'teamLifetimeCompletedOrders': 240, 'npcOwned': 4, 'ownedVehicleTierAtLeast': 'B', 'vehicleLevelAtLeast': 5, 'unlockFeeYuanCandidate': 1500},
                     {'map': 4, 'teamLifetimeCompletedOrders': 700, 'npcOwned': 8, 'ownedVehicleTierAtLeast': 'A', 'vehicleLevelAtLeast': 5, 'unlockFeeYuanCandidate': 4000},
                     {'map': 5, 'teamLifetimeCompletedOrders': 1800, 'npcOwned': 14, 'ownedVehicleTierAtLeast': 'SS', 'vehicleLevelAtLeast': 5, 'unlockFeeYuanCandidate': 10000}],
    },
    'subtables': {'pricing': '../2026-11-01-vehicle-economy/pricing-candidate.json',
                 'growth': '../2026-11-01-vehicle-growth/candidate.json',
                 'progressionTasks': '../2026-11-02-progression-tasks/candidate.json'},
    'reviewRequired': ['four-final-product-decisions-see-finalization-checklist', 'six-page-preview-and-unified-product-v2-review',
                       'pm-unified-stage-values-and-growth-budgets-including-task-rewards-and-map-fees'],
}

train_costs = {str(level): rnd(D(1800) * level * (level - 1) / 435) for level in [10, 20, 30]}
sss = growth['vehicles'][-1]['levels'][-1]
speed = D(sss['speedKph'])
vehicle_income = D(sss['totalVehicleIncomeMultiplier'])
normal_cycle = D(63) * 12 / speed + 27
trained_cycle = D(63) * 12 / speed + D(27) * D('0.85')
normal_income_hour = D(10) * vehicle_income * 3600 / normal_cycle
trained_income_hour = D(10) * vehicle_income * D('1.20') * 3600 / trained_cycle
base_assets = sum(x['recruitmentPriceYuan'] for x in prices['recruitment']) + 31 * (prices['vehicles'][-1]['purchasePriceYuan'] + prices['vehicles'][-1]['levels'][-1]['cumulativeUpgradeYuan'])
lower_payout = D(10) * D('0.75') * D('0.50')
report = {
    'status': 'candidate-closed-form-arithmetic-not-game-tests-or-measured-balance',
    'npcTrainingCumulativeYuan': train_costs,
    'all30NpcTrainingToMaxYuan': train_costs['30'] * 30,
    'recruitmentAndAll31SssMaxAssetBudgetYuan': base_assets,
    'sameAssetsPlusAllNpcTrainingYuan': base_assets + train_costs['30'] * 30,
    'base10LateAndSevereDamageActualIncomeCents': rnd(lower_payout * 100),
    'sameSingleOrderNetAfterMealCents': rnd((lower_payout - 3) * 100),
    'sameSingleOrderNetAfterTwoWatersCents': rnd((lower_payout - 2) * 100),
    'npcSssMaxUntrainedGrossYuanPerHour': rnd(normal_income_hour),
    'npcSssMaxTrainedGrossYuanPerHour': rnd(trained_income_hour),
    'fleet30TrainedSssMaxGrossYuanPerHour': rnd(trained_income_hour * 30),
    'allArithmeticExcludesRealRoutesRandomDistributionsOfflineLimitsAndUserPlay': True,
}
ROOT.mkdir(parents=True, exist_ok=True)
(ROOT / 'parameter-candidate.json').write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'arithmetic.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
print('只生成产品建议和设计算术；未调用游戏、测试、构建、浏览器或存档。')
