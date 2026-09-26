"""공공데이터포털(data.go.kr) '파일데이터'를 웹페이지의 [다운로드] 버튼과 동일한 공개 경로로 내려받는 헬퍼.
- 로그인/인증키가 필요 없는 공개 파일만 대상으로 한다(이용허락범위 제한 없음 데이터).
"""
import re, json, sys, pathlib, requests

UA = {"User-Agent": "Mozilla/5.0 (research; mobility-gap-ai)"}

def datagokr_download(public_data_pk: str, out_dir: str) -> pathlib.Path:
    s = requests.Session(); s.headers.update(UA)
    page = s.get(f"https://www.data.go.kr/data/{public_data_pk}/fileData.do", timeout=60).text
    m = re.search(r"fn_fileDataDown\('(\d+)',\s*'([^']+)',\s*'([^']*)',\s*'(\d+)'", page)
    if not m:
        raise RuntimeError("download button params not found")
    pk, detail_pk, atch, sn = m.groups()
    r = s.post("https://www.data.go.kr/tcs/dss/selectFileDataDownload.do",
               data={"publicDataDetailPk": detail_pk, "publicDataPk": pk, "atchFileId": atch,
                     "fileDetailSn": sn, "publicDataTyCode": "PR0051"}, timeout=60)
    j = json.loads(r.text)
    if not j.get("status"):
        raise RuntimeError(f"download refused: {j}")
    atch_id, file_sn = j["atchFileId"], j["fileDetailSn"]
    name = j["dataSetFileDetailInfo"].get("dataNm") or pk
    ext = j["dataSetFileDetailInfo"].get("atchFileExtsn") or j["dataSetFileDetailInfo"].get("fileExtsn") or ""
    url = f"https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId={atch_id}&fileDetailSn={file_sn}&dataNm={name}"
    resp = s.get(url, timeout=600)
    cd = resp.headers.get("Content-Disposition", "")
    fn = None
    mm = re.search(r"filename\*?=(?:UTF-8'')?\"?([^\";]+)", cd)
    if mm:
        from urllib.parse import unquote
        fn = unquote(mm.group(1))
        try:
            fn = fn.encode("latin-1").decode("utf-8")
        except Exception:
            pass
    if not fn:
        fn = f"{public_data_pk}.{ext or 'bin'}"
    out = pathlib.Path(out_dir) / fn
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(resp.content)
    meta = {"publicDataPk": pk, "atchFileId": atch_id, "fileDetailSn": file_sn, "dataNm": name,
            "page": f"https://www.data.go.kr/data/{public_data_pk}/fileData.do", "file": out.name,
            "bytes": len(resp.content)}
    (pathlib.Path(out_dir) / f"{public_data_pk}_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    return out

if __name__ == "__main__":
    p = datagokr_download(sys.argv[1], sys.argv[2])
    print(p, p.stat().st_size)
