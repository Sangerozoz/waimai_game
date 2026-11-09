# PM/B真实接入契约（stage，未编译/未实测）

所有源码位于本目录assets/scripts；下列导出/方法已经存在，不是待实现提案。唯一profile：capacity-slots-economy-2026-11-06-v1。

## 容量与候选
- domain/V2LoadRules.ts：V2Load为`{version:'kg-v1',weightKg:number}`或`{version:'slots-v1',occupiedSlots:1|2}`；V2Capacity相应为capacityKg或整数capacitySlots。parseV2Load/parseV2Capacity严格解析；fitsV2Capacity拒绝跨单位。
- runtime.normalCandidates(count=8)继续返回单个连续列表。新候选是V2FoodOffer：id/kind/sourceOfferId/pickupNode/dropoffNode/pickupName/dropoffName/load/food；新候选没有weightKg。food仍是原food-risk-v1三字段，不塞容量。
- 请求量由整数容量固定为min(50,max(8,2*capacitySlots))；count保留调用签名但新规则以该公式为准。相同池与ID占用稳定，扩大读取只继续有限扫描；不增加分页UI、不承诺装满或每级多一餐。
- 选择/传回订单时保留load与sourceOfferId；不要从旧kg或FoodItem.unitWeightKg构造它们。acceptBatch会校验源身份/端点和必需load，再白名单生成可信条款，不信caller价格/派生属性。

## 真实Runtime只读方法（V2RuntimeController.ts:161—170）
- `deliveryEffects`：当前已签主角行程的profileId、speedRelativeToStarter、incomeFactor、capacity。旧kg活单继续回capacity.version='kg-v1'；无车或未就绪回null。
- `nextBatchEffects`：下一未签新批的profileId、capacity/整数capacitySlots、speedRelativeToStarter、incomeFactor；无车/未就绪回null。
- `vehicleEffects(vehicleId)`：拥有车辆的新profile效果或null。
- `riderEffects(riderId)`：NPC的新profile incomeFactor/baseIncomeFactor/fixedServiceReduction或null；不用于主角XP等级。
- `vehicleUpgradeQuote(vehicleId)`、`riderUpgradeQuote(riderId)`：costCents/current/next/nextLevel；新profile另有fromLevel/toLevel/profileId；满级回null。NPC接口不接受hero。费用与实际扣款共用同一个quote路径，不在UI重算旧曲线。
- 收入/费用均为整数分；速度为相对初始车倍数；fixedServiceReduction是已省比例（0表示省时0%，不是耗时0%）。capacitySlots/occupiedSlots是整数格。主角收入经验仍由heroExperience与quote.xpMultiplier锁定，不把NPC培养表套给主角。

## 已签quote与legacy判别
- domain/V2EconomySession.ts导出contractTerms、legacyQuotePayload、validateSlotDeliveryQuote、validateSlotFleetQuote；acceptSlotBatch与registerSlotFleetOrders真实存在。
- 新quote.terms.version='slots-v1'，必须完整包含profileId/pricePolicyId/effectPolicyId/load/capacity/vehicleLevel/riderLevel/speedRelativeToStarter/incomeFactor/riderIncomeFactor/fixedServiceReduction。riderLevel是拥有对象的保存等级；主角的收入XP单独见xpMultiplier。ordinaryPricing.version='distance-effort-slots-v1'且有可信deliveryMetres；专送无ordinaryPricing。
- 旧quote保留原weightKg及全部原属性，只添加`terms:{version:'kg-v1',profileId:旧V2_CONFIG_ID}`。legacyQuotePayload仅去掉该标记，得到原payload；不会补造历史缺少的属性，不将旧重量取整成格。新容器缺terms绝不走legacy。
- 旧vehicleEffects/riderEffects/vehicleUpgradeQuote等旧导出仍是旧profile验证器。B的新展示用上述Runtime方法或显式slot前缀helpers，不能因名字相近继续用旧公式。

## 组合与生命周期
- 新写Game6(profileId、routeLoadProfile必需)/Route3/Dispatch2/Economy2/Fleet2；允许Game6内明确kg-v1的原Route2旧活单。Trip2/3保留食品格式，新slot有单行程必须Trip3，缺food不能借旧版本降级。
- 普通当前报价读取quote.incomeCents；quoteCandidates仍为隔离草稿预览，不写live。原ETA三个字段与planned补给规则保持。
- NPC工作中允许培养/配置申请；旧合同仍占旧车并用旧grade/收入/服务/dueMs完成，新批才生效。主角活批换车/升级仍禁。不要因此新增常驻额度或延后生效文案。
- UI尚未接入；新slot候选无weightKg，不能同旧UI混发。PM须整体协调所有reader/writer，经独立门禁后应用十份代码，不能单发新writer。
