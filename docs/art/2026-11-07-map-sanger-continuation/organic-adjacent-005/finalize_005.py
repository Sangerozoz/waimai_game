"""Refresh only map-owned indexes, retaining prior artifacts and protection hashes."""
import hashlib
import json
import subprocess
from datetime import datetime,timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ROOT=HERE.parents[3]
RECEIPT=ROOT/'docs/team/handoffs/2026-11-07-map-codex-sanger/new-thread-receipt.json'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):return json.loads(p.read_text())


def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')


def main():
    now=datetime.now(timezone.utc).isoformat();prior=read(HERE/'history/start/artifact-manifest.json')
    allowed={'REPORT.md','budget-template.html','build_sampling_budget.py','continuation-plan.md','current-map-state.json','index.html','sampling-budget.json',
             'organic-layout-004/index.html','organic-layout-004/RESULT.md'}
    special={'organic-layout-004/index.html':'organic-layout-004-index.html','organic-layout-004/RESULT.md':'organic-layout-004-RESULT.md'}
    for n,r in prior['files'].items():
        p=HERE/'history/start'/special.get(n,n)if n in allowed else BASE/n
        assert p.is_file()and sha(p)==r['sha256']and p.stat().st_size==r['bytes'],('prior artifact or backup changed',n)
    assert sha(HERE/'history/start/new-thread-receipt.json')==prior['externalReceipt']['sha256']
    snap=read(ROOT/'docs/team/handoffs/2026-11-07-map-codex-sanger/map-protected-snapshot.json')
    for n,r in snap['files'].items():assert sha(ROOT/n)==r['sha256']and(ROOT/n).stat().st_size==r['bytes'],n
    check=read(HERE/'verification/static-checks.json');display=read(HERE/'verification/browser-display-checks.json');cli=read(HERE/'verification/tiled-cli-v2/result.json')
    assert check['status']=='passed-bounded-evidence-only'and all(x['passed']for x in check['checks'])
    assert len(display['checks'])==12 and all(x['passed']for x in display['checks'])
    assert read(HERE/'verification/browser-close.json')['state']=='closed'
    assert cli['commands']==6 and len(cli['exports'])==6 and all(x['RGBPixelExact']for x in cli['comparisons'])
    assert all(r['exitCode']==0 for r in read(HERE/'verification/tiled-cli-v2/commands.json'))
    for r in display['savedCaptures']:assert sha(HERE/'verification'/r['file'])==r['sha256']
    for r in cli['exports']:assert sha(HERE/'verification/tiled-cli-v2'/r['file'])==r['sha256']
    for rel,r in read(HERE/'generated-files.json').items():assert sha(HERE/rel)==r['sha256'],rel
    result=read(HERE/'result.json');pair=read(HERE/'actual-pair-graph.json')
    assert sha(HERE/'native.png')==result['sha256']
    approved=read(BASE/'organic-layout-004/user-review-001.json')
    assert approved['userArtApproved']and approved['sha256']==sha(BASE/'organic-layout-004/native.png')
    review_path=HERE/'independent-review.json'
    review=read(review_path)if review_path.exists()else {'status':'requested-pending','threadId':'thr_978x3n893w'}
    checks={'recordedAt':now,'status':'passed-bounded-artifact-and-display-checks','nativeSize':[1671,941],'nativeSHA256Matched':True,
            'nativeBytesCopiedExactly':True,'inputFingerprintsMatched':3,'staticChecks':check['checkCount'],'pairSegmentPairsExamined':6441,
            'priorArtifactCount':len(prior['files']),'priorAllowedOwnedUpdates':sorted(allowed),'allOtherPriorArtifactHashesMatched':True,
            'allowedPriorFilesArchivedWithMatchingSHA':True,'protectedFilesMatched':len(snap['files']),
            'officialTiledCommands':6,'officialTiledExports':6,'officialTiledVersion':cli['appVersion'],
            'backgroundRGBPixelExact':True,'backgroundAlphaAll255':True,'browserDisplayChecksPassed':12,'browserCapturesSaved':4,'browserSessionClosed':True,
            'independentReview':review,'fullStreetInventoryComplete':False,'wholeSeamReady':False,'completeObjectOwnershipResolved':False,
            'userArtApproved':False,'ordinaryRegionAdmitted':False,'formalGameTestsPerformed':False}
    write(HERE/'verification/increment-check.json',checks)
    write(HERE/'verification/protected-after.json',{'recordedAt':now,'filesChecked':len(snap['files']),'matched':len(snap['files']),'mismatches':[],
          'snapshot':'docs/team/handoffs/2026-11-07-map-codex-sanger/map-protected-snapshot.json'})
    sample={'source':'organic-adjacent-005/result.json','viewer':'organic-adjacent-005/index.html','nativeSize':[1671,941],
            'nativeSHA256':result['sha256'],'nativeBytes':result['bytes'],'designGuide':'organic-adjacent-005/structure-guide.json',
            'designOnlyBoundedFaces':6,'observedBuildingBearingEnclosures':5,'tracedBuildingBearingEnclosures':4,'channelizingIslandsExcludedFromBlocks':1,
            'exclusiveNewBlockOwnershipResolved':False,'actualRoadTraceCompleted':False,'fullStreetInventoryComplete':False,
            'actualCompleteBlockCount':None,'metreCalibration':None,'userArtApproved':False,'ordinaryRegionAdmitted':False}
    art004={'source':'organic-layout-004/result.json','viewer':'organic-layout-004/index.html','nativeSize':[1672,941],
            'nativeSHA256':approved['sha256'],'userArtApproved':True,'userArtReview':'organic-layout-004/user-review-001.json',
            'actualRoadTraceCompleted':False,'traceScope':'main street for005 connection only','ordinaryRegionAdmitted':False,'metreCalibration':None}
    roads={'source':'organic-adjacent-005/actual-pair-graph.json','context':'005 plus004 main-street partial trace on diagnostic assembly',
           'nativeSizes':[[1671,941],[1672,941]],'diagnosticAssemblySize':[3192,941],'nodes':26,'edges':30,'connectedComponents':1,'boundedFaces':5,
           '005TracedBuildingBearingEnclosures':4,'005ObservedBuildingBearingEnclosures':5,'channelizingIslandsExcludedFromBlockCount':1,
           'exclusiveNewBlockOwnershipResolved':False,'fullStreetInventoryComplete':False,'wholeSeamReady':False,'completeObjectOwnershipResolved':False,
           'mainRoutePixels':pair['routes']['main']['lengthPixels'],'alternativeRoutePixels':pair['routes']['alternative']['lengthPixels'],
           'excludedEdge':'W-M1--ML','geometricBidirectionalAssumption':True,'trafficDirectionValidated':False,'metreCalibration':None,
           'ordinaryRegion':False,'userArtApproved':False}
    next_action='Present005 native for user art review. Preserve004. Before claiming seam-ready, assign complete shared objects and inspect each seam segment; current rectangle remains diagnostic. Do not generate another image before005 review; no D/legacy queue or formal game tests.'
    state=read(BASE/'current-map-state.json')
    oldstate=read(HERE/'history/start/current-map-state.json')
    state.setdefault('previousAdjacentPairRoadEvidence',oldstate['actualRoadEvidence'])
    state.setdefault('previousAdjacentPairVerification',oldstate['verification'])
    state.setdefault('previousOrganic004Verification',oldstate['currentIncrementVerification'])
    state.update(recordedAt=now,status='005-native-and-partial-road-evidence-ready-for-art-review-seam-unresolved',
                 imageRequestsSinceHandoff=6,newImagesReturnedSinceHandoff=5,imageRequestsThisIncrement=1,imagesReturnedThisIncrement=1,
                 latestImageAssessment='organic-adjacent-005/RESULT.md',latestArtworkCandidate=sample,lastUserApprovedArtwork=art004,
                 actualRoadEvidence=roads,verification=checks,currentIncrementVerification=checks,nextAction=next_action)
    if 'organic-adjacent-005/result.json'not in state['imageAttemptRecords']:state['imageAttemptRecords'].append('organic-adjacent-005/result.json')
    state['blockingEvidence']=[
        '005 is awaiting user art review;004 art is approved. Current native return1671x941 does not establish4K or accepted near-view sampling.',
        '005 shared buildings were redrawn. Whole-seam registration and complete-object ownership remain unresolved; rectangular assembly is diagnostic only.',
        'Partial graph proves four005 building-bearing enclosures plus one island; visual inventory observes five, shared enclosure is not an exclusive new block.',
        '004 full tracing, traffic semantics, credible metre coverage and final image count remain incomplete.20–24 is conditional arithmetic only.',
    ]
    state['layoutCorrection'].update(status='004-user-art-approved-005-organic-adjacent-awaiting-art-review',latestContinuation='organic-adjacent-005/DESIGN.md')
    newoutputs=['organic-adjacent-005/index.html','organic-adjacent-005/RESULT.md','organic-adjacent-005/tiled/native005.tmj',
                'organic-adjacent-005/tiled/native004-partial.tmj','organic-adjacent-005/tiled/organic-pair.tmj','organic-layout-004/user-review-001.json']
    state['outputs']=newoutputs+[n for n in state['outputs']if n not in newoutputs]
    write(BASE/'current-map-state.json',state)
    receipt=read(RECEIPT);receipt['lastUpdatedAt']=now
    receipt['currentStage'].update(stage=state['status'],newImageToolRequests=6,newImagesReturned=5,latestNativeSize=[1671,941],
        latestNativeSizes=[[1671,941],[1672,941]],latestAssemblySize=[3192,941],assemblyIsDiagnosticOnly=True,wholeSeamReady=False,
        actualStandaloneTraceNodes=26,actualStandaloneTraceEdges=30,permittedNavigationEdges=30,occludedInferenceEdges=0,
        actualStandaloneTraceContext='005 plus004 main-street partial trace; not complete inventory or object-owned city assembly')
    receipt.update(nextConcreteAction=next_action,latestArtworkCandidate=sample,lastUserApprovedArtwork=art004,layoutCorrection=state['layoutCorrection'])
    receipt['verification']['organicAdjacent005Increment']=checks
    receipt['protectionCheck'].update(matchedAfterWork=91,afterReport='docs/art/2026-11-07-map-sanger-continuation/organic-adjacent-005/verification/protected-after.json')
    cap=receipt['workPerformed']['currentBuiltInImageCapabilityProof'];cap.update(attemptsSinceHandoff=6,successfulImages=5,latestNativeSHA256=result['sha256'],latestNativeBytes=result['bytes'])
    if 'organic005 image returned1671x941RGB'not in cap['attemptResults']:cap['attemptResults'].append('organic005 image returned1671x941RGB')
    receipt['workPerformed']['organicLayoutCandidate']=art004;receipt['workPerformed']['organicAdjacent005']={'artwork':sample,'partialRoads':roads,'verification':checks}
    for rel in newoutputs:
        n=str((BASE/rel).relative_to(ROOT))
        if n not in receipt['newCurrentEntrances']:receipt['newCurrentEntrances'].append(n)
    for rel in ['PLAN.md','DESIGN.md','RESULT.md','INDEPENDENT-PREFLIGHT.md']:
        n=str((HERE/rel).relative_to(ROOT))
        if n not in receipt['readEntrances']:receipt['readEntrances'].append(n)
    write(RECEIPT,receipt)
    report=(BASE/'REPORT.md').read_text()
    intro='当前画面入口是 `organic-layout-004/index.html`。用户最新要求“不可以太规整”，现已重做局部道路/地块组织并实际生成一张新原生1672×941，待用户审画。上轮 `adjacent-pair-003`保留拼接/导航技术证据，格子构图不再沿用扩城。普通地图地区仍为A2/B1/C。'
    report=report.replace(intro,'当前画面入口是 `organic-adjacent-005/index.html`。004已获用户明确美术认可，西邻005已生成原生1671×941，待审画。部分可见沥青描线、Tiled与网页证据齐备；共享楼体归属未核，矩形接续仍为诊断。W/E格子构图不作扩城模板，普通地图地区仍为A2/B1/C。',1)
    marker='\n## 最新：曲折道路与多变街坊结构纠偏004\n'
    if marker in report:report=report.replace(marker,'\n## 004生成阶段记录（后续已获用户美术认可）\n',1)
    start='\n<!-- organic005-current:start -->\n';end='<!-- organic005-current:end -->\n'
    section=start+'## 当前：004认可后的西邻005\n\n用户原话“这版地图认可，做的还不错，继续吧。”绑定004原生SHA，记录在`organic-layout-004/user-review-001.json`。本轮顺序生成一张005，未扩下一张；原生RGB1671×941、3,986,067字节、SHA `'+result['sha256']+'`，原字节保存。接续累计6请求/5成功，005少返回1列未拉伸补齐。\n\n原图独立预检观察5处楼群道路围合；当前部分描线证明4处＋1导流岛，右上共享围合未纳入图且未核为独占新增。设计通道变成庭院/棚顶的部分排除导航。与004主路合26节点/30边/1连通分量，6441对线段无异常交叉，主路径3104.1345px、断边绕行3605.3343px；双向是假设，米数未知。\n\n共享151×941带只有48像素完全相同；建筑和棚顶被重画，不能整带直接认定配准。3192×941矩形拼图仅接续诊断，完整对象归属仍未核；三处共同沥青点不是中心线零残差。005待用户审画，004完整路网未完成。\n\n当前'+str(check['checkCount'])+'文件/几何检查、官方Tiled1.12.2六命令/六导出及网页12项显示检查通过，四截图已保存，浏览器已关闭。三张纯底图RGB逐像素相同；91保护源保持。原失败和诊断限制在005目录保留；独立复核状态：'+review['status']+'。普通地图未增加，D未恢复，未做正式游戏测试。\n'+end
    if start in report:report=report[:report.index(start)]+section+report[report.index(end)+len(end):]
    else:report=report.replace('\n## 004生成阶段记录',section+'\n## 004生成阶段记录',1)
    old_next='用户已明确允许突破原4～6张PM预算，先做相邻两区；无需重新询问这项许可。两区的接缝/独立描路/导航技术证据保留，但最新城市结构要求已转向004的曲折道路和多变街坊。当前交004新原生及近景供用户审画，再完善地形驱动的全城骨架与完整街坊分图，并对实际可见路面重新描路。米制覆盖与最终图数仍未冻结。20～24只是假设下的矩形像素容量算例，不决定道路形状或出图数量；旧25队列不恢复，外围低采样也尚未采用。'
    report=report.replace(old_next,'用户已允许增图并认可004的曲折道路画面。当前交005供审画，先保留本张原生与部分描路证据；完整对象归属和逐段接缝须在称拼接就绪前完成。005尚未审画，不再生成下一张。整体米制覆盖与最终图数未冻结，20～24只是条件容量算例；旧队列和外围低采样均不恢复。',1)
    (BASE/'REPORT.md').write_text(report)
    (BASE/'continuation-plan.md').write_text('# 2026-11-07 地图主线接续执行\n\n当前主会话thr_fs5qphhxgc，Codex / ccs-sanger/gpt-6.1-sol / max，同checkout/分支，不续派旧Hermes队列。\n\n当前沿整区底图＋独立矢量描路继续。004用户美术认可已绑定原生SHA；只新增一张西邻005，实际1671×941，待审画。累计6请求/5成功，A2/B1/C仍为全部普通已入图地区，D未恢复。\n\n005当前部分路网证明4处楼群围合＋1导流岛，原图观察5处；共享围合独占归属未核。与004部分主路合26节点/30边。矩形接续只作诊断，共享建筑被重画，完整对象归属与整带配准尚未完成；源图不变，不重生以掩盖问题。\n\n当前入口`organic-adjacent-005/index.html`，具体证据见本张RESULT。设计与实际描路分开，Tiled/浏览器检查、用户审画、普通入图和游戏验收分层。\n\n下一动作：交005审画；在宣称拼接就绪前核定完整共享对象及逐段接缝。用户未审005前不生成下一张。目标约旧25面积1/4；无可信米制覆盖，最终图数未知，20～24仍只是条件算例。保留所有原生、旧路/边界/用户手调，未改产品/UI/经济/存档，未做正式游戏测试。\n')
    subprocess.run(['python3',str(BASE/'build_sampling_budget.py')],cwd=ROOT,check=True,capture_output=True,text=True)
    before=read(HERE/'history/start/sampling-budget.json');after=read(BASE/'sampling-budget.json')
    assert before['scenarios']==after['scenarios']and before['baseline']==after['baseline']
    assert after['imageRequestsSinceHandoff']==6 and after['successfulImagesSinceHandoff']==5
    for n,h in after['sourceSHA256'].items():assert sha(ROOT/n)==h,n
    for n,r in snap['files'].items():assert sha(ROOT/n)==r['sha256'],n
    manifest={'recordedAt':now,'scope':'map-only005 candidate, partial vector evidence and diagnostic assembly; no seamless city/game acceptance',
              'authorThread':'thr_fs5qphhxgc','externalReceipt':{'path':str(RECEIPT.relative_to(ROOT)),'sha256':sha(RECEIPT)},'files':{}}
    for p in sorted(BASE.rglob('*')):
        if p.is_file()and p!=BASE/'artifact-manifest.json'and '__pycache__'not in p.parts and p.name!='.DS_Store':
            manifest['files'][str(p.relative_to(BASE))]={'bytes':p.stat().st_size,'sha256':sha(p)}
    write(BASE/'artifact-manifest.json',manifest)
    print(json.dumps({'status':state['status'],'manifestFiles':len(manifest['files']),'protectedMatched':91,
                      'staticChecks':check['checkCount'],'browserChecks':12,'budgetScenariosUnchanged':True,'review':review['status']},ensure_ascii=False))


if __name__=='__main__':main()
