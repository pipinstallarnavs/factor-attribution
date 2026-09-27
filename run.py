import argparse,hashlib,io,json,urllib.request,zipfile
from pathlib import Path
import numpy as np,pandas as pd
import statsmodels.api as sm
ROOT=Path(__file__).parent
URL='https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip'
MOM='https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily_CSV.zip'
ME='https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Portfolios_Formed_on_ME_Daily_CSV.zip'
def french(url,name):
 p=ROOT/'data'/name; p.parent.mkdir(exist_ok=True)
 if not p.exists(): p.write_bytes(urllib.request.urlopen(url,timeout=30).read())
 with zipfile.ZipFile(p) as z: raw=z.read(z.namelist()[0]).decode('latin1').splitlines()
 start=next(i for i,l in enumerate(raw) if l[:8].strip().isdigit()); rows=[]
 for l in raw[start:]:
  if not l[:8].strip().isdigit(): break
  vals=l.split(','); rows.append([vals[0]]+[float(x) for x in vals[1:]])
 return pd.DataFrame(rows,columns=['Date','Mkt-RF','SMB','HML','RMW','CMA','RF']).assign(Date=lambda x:pd.to_datetime(x.Date,format='%Y%m%d')).set_index('Date')/1
def momentum():
 p=ROOT/'data'/'mom.zip'; p.parent.mkdir(exist_ok=True)
 if not p.exists(): p.write_bytes(urllib.request.urlopen(MOM,timeout=30).read())
 with zipfile.ZipFile(p) as z: raw=z.read(z.namelist()[0]).decode('latin1').splitlines()
 start=next(i for i,l in enumerate(raw) if l[:8].strip().isdigit()); return pd.Series({pd.to_datetime(l[:8],format='%Y%m%d'):float(l.split(',')[1]) for l in raw[start:] if l[:8].strip().isdigit()},name='Mom')
def size_portfolio():
 p=ROOT/'data'/'me.zip';p.parent.mkdir(exist_ok=True)
 if not p.exists():p.write_bytes(urllib.request.urlopen(ME,timeout=30).read())
 with zipfile.ZipFile(p) as z: raw=z.read(z.namelist()[0]).decode('latin1').splitlines()
 start=next(i for i,l in enumerate(raw) if l[:8].strip().isdigit()); out={}
 for l in raw[start:]:
  if not l[:8].strip().isdigit(): break
  vals=l.split(','); value=float(vals[2])  # value-weighted low 30% portfolio
  if value > -90: out[pd.to_datetime(l[:8],format='%Y%m%d')]=value
 return pd.Series(out,name='portfolio')/100
def run(window=252):
 f=french(URL,'factors.zip').join(momentum(),how='inner').dropna(); f=f/100
 # a real traded proxy; its return is independent of the factors in the fit window
 # The smallest-size portfolio is a separate real return series, not a factor input.
 df=f.join(size_portfolio(),how='inner').dropna(); y=df.portfolio-df.RF; X=sm.add_constant(df[['Mkt-RF','SMB','HML','RMW','CMA','Mom']]); split=int(len(df)*.7); rows=[]
 for end in range(split,min(len(df),split+1000)):
  lo=max(0,end-window); fit=sm.OLS(y.iloc[lo:end],X.iloc[lo:end]).fit(); pred=float(X.iloc[end]@fit.params); contrib=(X.iloc[end]*fit.params).to_dict(); contrib['realized']=float(y.iloc[end]); contrib['residual']=float(y.iloc[end]-pred); contrib['date']=str(df.index[end].date()); rows.append(contrib)
 out=pd.DataFrame(rows); return {'n':len(df),'train':split,'holdout':len(out),'mean_abs_residual':float(out.residual.abs().mean()),'exposure_mean':{k:float(out[k].mean()) for k in ['Mkt-RF','SMB','HML','RMW','CMA','Mom']},'reconciliation_max_error':float(np.max(np.abs(out.realized-(out[['const','Mkt-RF','SMB','HML','RMW','CMA','Mom','residual']].sum(axis=1))))),'rows':rows[:3]}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--window',type=int,default=252); a=ap.parse_args(); r=run(a.window); (ROOT/'results').mkdir(exist_ok=True); (ROOT/'results/report.json').write_text(json.dumps(r,indent=2)); print(json.dumps(r,indent=2))
if __name__=='__main__':main()
