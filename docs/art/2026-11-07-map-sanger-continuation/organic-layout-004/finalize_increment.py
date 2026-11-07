"""Record this bounded artwork increment and refresh only its map-owned indexes."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ROOT=HERE.parents[3]
RECEIPT=ROOT/'docs/team/handoffs/2026-11-07-map-codex-sanger/new-thread-receipt.json'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def write_json(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')


def main():
    now=datetime.now(timezone.utc).isoformat()
    old=json.loads((HERE/'history/before-structure-correction/artifact-manifest.json').read_text())
    allowed={'REPORT.md','budget-template.html','build_sampling_budget.py','continuation-plan.md',
             'current-map-state.json','index.html','sampling-budget.json'}
    for n,r in old['files'].items():
        if n in allowed:
            backup=HERE/'history/before-structure-correction'/n
            if not backup.exists():
                original=subprocess.run(['git','show','651b5263c8d77e7857ae7786c36a3ef422bfee63:'+str((BASE/n).relative_to(ROOT))],cwd=ROOT,check=True,capture_output=True).stdout
                assert hashlib.sha256(original).hexdigest()==r['sha256']
                with backup.open('xb') as f:f.write(original)
            assert sha(backup)==r['sha256']
        else:
            assert sha(BASE/n)==r['sha256'],f'Unplanned old artifact change: {n}'
    assert sha(RECEIPT)==old['externalReceipt']['sha256']
    protected=json.loads((ROOT/'docs/team/handoffs/2026-11-07-map-codex-sanger/map-protected-snapshot.json').read_text())
    for n,r in protected['files'].items():
        assert sha(ROOT/n)==r['sha256'] and (ROOT/n).stat().st_size==r['bytes'],n
    result=json.loads((HERE/'result.json').read_text())
    assert sha(HERE/'native.png')==result['sha256']
    assert (HERE/'native.png').read_bytes()==Path(result['toolDefaultOutputPath']).read_bytes()
    with Image.open(HERE/'native.png') as im: assert list(im.size)==result['actualSize']==[1672,941] and im.mode=='RGB'
    inputs=json.loads((HERE/'input-fingerprints.json').read_text())
    for ref in inputs:
        assert sha(ROOT/ref['path'])==ref['sha256'] and (ROOT/ref['path']).stat().st_size==ref['bytes']
    request={'recordedAt':now,'tool':'image_gen.imagegen','mode':'built-in','intent':'new local map artwork from references',
             'promptFile':'prompt.txt','promptSHA256':sha(HERE/'prompt.txt'),
             'transparent_background':False,'referenced_image_paths':[str(ROOT/r['path']) for r in inputs],
             'inputFingerprints':'input-fingerprints.json','canvasRequestedInPrompt':[1672,941],
             'independentToolSizeParameterAvailable':False,'newBackendOrCredentialChanges':False,
             'actualResult':'result.json','generationBackendModelNotExposed':True}
    with (HERE/'request-record.json').open('x') as f:json.dump(request,f,ensure_ascii=False,indent=2);f.write('\n')
    browser=json.loads((HERE/'verification/browser-result.json').read_text())
    display=json.loads(browser['text'].split('ORGANIC_DISPLAY_CHECKS=',1)[1])
    assert browser['exitCode']==0 and len(display['checks'])==5 and all(x['passed'] for x in display['checks'])
    assert json.loads((HERE/'verification/browser-close.json').read_text())['state']=='closed'
    guide=json.loads((HERE/'structure-check.json').read_text())
    assert guide['status']=='passed-design-only' and not guide['unexpectedCrossingsOrOverlaps']
    checks={'recordedAt':now,'status':'passed-bounded-artifact-and-display-checks',
            'nativeSHA256Matched':True,'nativeBytesCopiedExactly':True,'nativeSize':[1672,941],
            'inputFingerprintsMatched':len(inputs),'protectedFilesMatched':len(protected['files']),
            'priorArtifactCount':len(old['files']),'priorAllowedOwnedUpdates':sorted(allowed),
            'allOtherPriorArtifactHashesMatched':True,'designSegmentPairsExamined':guide['pairsExamined'],
            'designBoundedFaces':guide['independentBoundedFaces'],'actualImageRoadTracingCompleted':False,
            'actualImageCompleteBlockCountCertified':False,'browserDisplayChecksPassed':5,
            'browserCapturesSaved':len(browser['images']),'browserSessionClosed':True,
            'userArtApproved':False,'ordinaryRegionAdmitted':False,'formalGameTestsPerformed':False}
    write_json(HERE/'verification/increment-check.json',checks)
    write_json(HERE/'verification/protected-after.json',{'recordedAt':now,'filesChecked':len(protected['files']),
                'matched':len(protected['files']),'mismatches':[],'snapshot':'docs/team/handoffs/2026-11-07-map-codex-sanger/map-protected-snapshot.json'})

    sample={'source':'organic-layout-004/result.json','viewer':'organic-layout-004/index.html',
            'nativeSize':[1672,941],'nativeSHA256':result['sha256'],'nativeBytes':result['bytes'],
            'designGuide':'organic-layout-004/structure-guide.json','designCheck':'organic-layout-004/structure-check.json',
            'designOnlyBoundedFaces':8,'actualRoadTraceCompleted':False,'actualCompleteBlockCount':None,
            'metreCalibration':None,'userArtApproved':False,'ordinaryRegionAdmitted':False}
    correction={'directUserQuote':json.loads((HERE/'authorization.json').read_text())['directUserQuote'],
                'record':'organic-layout-004/DESIGN.md','status':'applied-to-new-local-artwork-candidate',
                'previousPairGridApprovedForCityProduction':False,
                'finalCityRoadLayoutOrImagePartitionFrozen':False}
    state=json.loads((BASE/'current-map-state.json').read_text())
    state.update(recordedAt=now,status='organic-structure-native-returned-awaiting-user-art-review',
                 imageRequestsSinceHandoff=5,newImagesReturnedSinceHandoff=4,imageRequestsThisIncrement=1,
                 imagesReturnedThisIncrement=1,latestImageAssessment='organic-layout-004/RESULT.md',
                 latestArtworkCandidate=sample,layoutCorrection=correction,currentIncrementVerification=checks)
    state['imageAttemptRecords'].append('organic-layout-004/result.json')
    state['actualRoadEvidence']['context']='previous adjacent-pair-003 technical sample; not organic-layout-004 tracing'
    state['verification']['context']='previous adjacent-pair-003; current increment has separate artifact/display checks'
    state['separateInheritedPlanning']['roadLayoutStatus']='quantity/loop organization baseline, not a final grid or user-approved road shape'
    state['outputs']=['organic-layout-004/index.html','organic-layout-004/RESULT.md','organic-layout-004/DESIGN.md']+state['outputs']
    state['blockingEvidence']=[
        'Native return remains1672x941; no verified4K or accepted near-view sampling/metre coverage.',
        'New organic layout is an artwork candidate; actual tracing, adjacent organic samples and user art review remain pending.',
        'Related residential facade vocabulary and some warm window details remain in004.',
        'Increased-count route is authorized; final count is unknown, and20–24 remains conditional capacity arithmetic.',
    ]
    state['nextAction']='Present004 organic-road candidate and native detail for art/structure review. Then refine terrain-led whole-city skeleton and complete-block image partitions, trace the actual visible asphalt with occlusion exclusions, and verify new Tiled/navigation separately. Do not extend the W/E grid or restart D/legacy queues.'
    write_json(BASE/'current-map-state.json',state)
    receipt=json.loads(RECEIPT.read_text())
    receipt['lastUpdatedAt']=now
    receipt['currentStage'].update(stage=state['status'],newImageToolRequests=5,newImagesReturned=4,
                                   latestNativeSize=[1672,941],actualStandaloneTraceContext='previous adjacent-pair-003 only;004 actual tracing pending')
    receipt['nextConcreteAction']=state['nextAction']; receipt['latestArtworkCandidate']=sample; receipt['layoutCorrection']=correction
    receipt['verification']['organicArtworkIncrement']=checks
    receipt['protectionCheck'].update(matchedAfterWork=91,afterReport='docs/art/2026-11-07-map-sanger-continuation/organic-layout-004/verification/protected-after.json')
    cap=receipt['workPerformed']['currentBuiltInImageCapabilityProof']
    cap.update(attemptsSinceHandoff=5,successfulImages=4,latestNativeSHA256=result['sha256'],latestNativeBytes=result['bytes'])
    cap['attemptResults'].append('organic004 image returned1672x941RGB')
    receipt['workPerformed']['organicLayoutCandidate']=sample
    for n in ['organic-layout-004/DESIGN.md','organic-layout-004/RESULT.md','organic-layout-004/index.html']:
        path=str((BASE/n).relative_to(ROOT));receipt['newCurrentEntrances'].append(path)
    write_json(RECEIPT,receipt)
    report=(BASE/'REPORT.md').read_text()
    old_intro='最新独立实测入口是 `adjacent-pair-003/index.html`。用户“允许”已批准增图路线，现新产相邻W/E两区原生，各1672×941、六完整街坊，按道路裁界拼成3248×937。普通地图地区仍为A2/B1/C；下面第一轮八街坊及预算证据继续保留。'
    new_intro='当前画面入口是 `organic-layout-004/index.html`。用户最新要求“不可以太规整”，现已重做局部道路/地块组织并实际生成一张新原生1672×941，待用户审画。上轮 `adjacent-pair-003`保留拼接/导航技术证据，格子构图不再沿用扩城。普通地图地区仍为A2/B1/C。'
    assert old_intro in report
    report=report.replace(old_intro,new_intro,1)
    section='\n## 最新：曲折道路与多变街坊结构纠偏004\n\n实际查看旧25图名义总图、TR22/TR24、用户原图与A2密度局部后，采用弯曲主路、错位T形接入、楔形公园与沿河街坊。新原生RGB1672×941，4,120,033字节，SHA256 `'+result['sha256']+'`；原件逐字节入库，无本地重采样或滤色。接续累计5请求、4成功。提示词、输入角色/SHA、原生和新旧对照页均在004目录。\n\n底稿16节点/23边/8围合、608856对线段无异常，仅为像素设计；不计作新图实际描路。浏览器已实际解码三幅对照，5项显示检查通过，保存适宽/原生近景/375CSSpx三截图并关闭会话。新图完整描路、Tiled和导航留待本张结构/画面审阅后另做；住宅立面语言相近及局部暖窗如实保留待审。91保护源SHA仍全部一致。\n\n整体目标、米制覆盖未知、最终图数未定及4K缺口保持。矩形铺幅表仅作像素容量算例，不能决定路型。004未入普通地图、未用户验收，无正式游戏测试。\n'
    marker='\n## 接续第一阶段图像尝试'
    report=report.replace(marker,section+marker,1)
    report=report.replace('## 本轮相邻两区实测','## 前轮相邻两区实测（技术证据保留）')
    report=report.replace('接续以来4次实际请求、3张成功返回，首轮502失败保留。','该阶段接续累计4次实际请求、3张成功返回，首轮502失败保留。')
    old_next='用户已明确允许突破原4～6张PM预算，先做相邻两区；无需重新询问这项许可。两区已完成实际原生/接缝/独立描路与导航显示，当前把修复后的实物交用户审画。住宅语言相近、部分店面偏暖亮和原生细节限制仍披露；米制覆盖与最终图数未冻结。20～24只是375CSSpx/120m等假设下的规则铺幅示例，不是已批准的精确生产图数，不恢复旧25图队列。外围低采样敏感性也尚未采用。'
    new_next='用户已明确允许突破原4～6张PM预算，先做相邻两区；无需重新询问这项许可。两区的接缝/独立描路/导航技术证据保留，但最新城市结构要求已转向004的曲折道路和多变街坊。当前交004新原生及近景供用户审画，再完善地形驱动的全城骨架与完整街坊分图，并对实际可见路面重新描路。米制覆盖与最终图数仍未冻结。20～24只是假设下的矩形像素容量算例，不决定道路形状或出图数量；旧25队列不恢复，外围低采样也尚未采用。'
    report=report.replace(old_next,new_next,1)
    (BASE/'REPORT.md').write_text(report)
    budget_run=subprocess.run(['python3',str(BASE/'build_sampling_budget.py')],cwd=ROOT,capture_output=True,text=True,check=True)
    before=json.loads((HERE/'history/before-structure-correction/sampling-budget.json').read_text())
    after=json.loads((BASE/'sampling-budget.json').read_text())
    assert before['scenarios']==after['scenarios'] and before['baseline']==after['baseline']
    assert after['imageRequestsSinceHandoff']==5 and after['successfulImagesSinceHandoff']==4
    for n,expected in after['sourceSHA256'].items():assert sha(ROOT/n)==expected
    # Recheck protection after every index/receipt write, then seal the manifest.
    for n,r in protected['files'].items():assert sha(ROOT/n)==r['sha256'],n
    manifest={'recordedAt':now,'scope':'map-only continuation; organic004 artwork candidate plus preserved technical evidence/histories; no city/game/user acceptance',
              'authorThread':'thr_fs5qphhxgc','externalReceipt':{'path':str(RECEIPT.relative_to(ROOT)),'sha256':sha(RECEIPT)},
              'files':{}}
    for p in sorted(BASE.rglob('*')):
        if p.is_file() and p!=BASE/'artifact-manifest.json' and '__pycache__' not in p.parts and p.name!='.DS_Store':
            manifest['files'][str(p.relative_to(BASE))]={'bytes':p.stat().st_size,'sha256':sha(p)}
    write_json(BASE/'artifact-manifest.json',manifest)
    print(json.dumps({'status':state['status'],'manifestFiles':len(manifest['files']),'protectedMatched':91,
                      'newNativeSHA256':result['sha256'],'browserDisplayChecks':5,'budgetArithmeticScenariosUnchanged':True}))


if __name__=='__main__':main()
