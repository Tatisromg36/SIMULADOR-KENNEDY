import json, base64, math, numpy as np
from shapely.geometry import Polygon, MultiPoint, Point
from shapely import minimum_rotated_rectangle

SRC="/tmp/claude-0/-home-claude/cfc7817e-714b-5710-ba68-4b14d8c3b130/scratchpad/sim_in/SIMULACI#U00d3N/POLIGONO SI.geojson"
LON0,LAT0=-74.1585,4.6315
KX=111320*math.cos(math.radians(LAT0)); KY=110574.0
def disp(px,py):  # masterplan pixel (as displayed, 2000 wide) -> meters east/north
    return ((px*1.0235-1040.97)*3.6459, -(py*1.0235-1188.89)*3.6459)

d=json.load(open(SRC))
bx=[];by=[];bw=[];bd=[];ba=[];bf=[];barea=[]
for f in d["features"]:
    fl=f["properties"]["CONNPISOS"] or 1
    for poly in f["geometry"]["coordinates"]:
        if not poly or len(poly[0])<4: continue
        ring=np.array(poly[0])
        x=(ring[:,0]-LON0)*KX; y=(ring[:,1]-LAT0)*KY
        area=0.5*abs(np.dot(x[:-1],y[1:])-np.dot(x[1:],y[:-1]))
        if area<20: continue
        try:
            r=minimum_rotated_rectangle(Polygon(np.c_[x,y]))
            c=np.array(r.exterior.coords)
        except Exception: continue
        e1=c[1]-c[0]; e2=c[2]-c[1]
        w=np.hypot(*e1); dd=np.hypot(*e2)
        if w<1 or dd<1: continue
        th=math.atan2(e1[1],e1[0])%math.pi
        cx,cy=c[:4,0].mean(),c[:4,1].mean()
        bx.append(cx);by.append(cy);bw.append(w);bd.append(dd);ba.append(th);bf.append(min(max(int(fl),1),30));barea.append(area)
bx=np.array(bx);by=np.array(by);bw=np.array(bw);bd=np.array(bd);ba=np.array(ba);bf=np.array(bf);barea=np.array(barea)
N=len(bx); print("buildings",N)
rect=minimum_rotated_rectangle(MultiPoint(np.c_[bx,by]).convex_hull)
rect_pts=[list(map(float,p)) for p in list(rect.exterior.coords)[:4]]
print("rect",rect_pts)

# grid
CS=100.0; X0,Y0,X1,Y1=-4000.0,-2000.0,4400.0,5100.0
nx=int((X1-X0)/CS); ny=int((Y1-Y0)/CS)
gx=X0+(np.arange(nx)+0.5)*CS; gy=Y0+(np.arange(ny)+0.5)*CS
GX,GY=np.meshgrid(gx,gy)   # shape ny,nx
rb=rect.buffer(60)
mask=np.zeros((ny,nx),bool)
from shapely import contains_xy
mask=contains_xy(rb,GX,GY)
ix=np.clip(((bx-X0)/CS).astype(int),0,nx-1); iy=np.clip(((by-Y0)/CS).astype(int),0,ny-1)
area=np.zeros((ny,nx)); gfa=np.zeros((ny,nx)); np.add.at(area,(iy,ix),barea); np.add.at(gfa,(iy,ix),barea*bf)
cov=np.clip(area/(CS*CS),0,1); gfa=gfa/(CS*CS)

# geometry from the masterplan (displayed pixel coords)
P=lambda pts:[list(disp(*p)) for p in pts]
lines={
 "cra86":P([(660,1245),(900,1030),(1180,790),(1420,560),(1690,335)]),
 "calle6":P([(1115,1155),(1400,1168),(1700,1190),(2000,1218)]),
 "sw1":P([(830,1255),(870,1235),(905,1215)]),
 "se1":P([(1030,1335),(1135,1420)]),
}
import cv2
_wp=json.load(open("/tmp/claude-0/-home-claude/cfc7817e-714b-5710-ba68-4b14d8c3b130/scratchpad/work/wet_px.json"))
def _w(poly): return [[(x-1040.97)*3.6459, -(y-1188.89)*3.6459] for x,y in poly]
# lago La Magdalena desde la imagen
_im=cv2.imread("/tmp/claude-0/-home-claude/cfc7817e-714b-5710-ba68-4b14d8c3b130/scratchpad/mp/mp-1.png")
_B,_G,_R=[_im[...,i].astype(int) for i in range(3)]
_cy=((_R<140)&(_G>175)&(_B>185)&(_G-_R>55)).astype(np.uint8)*255
_m=np.zeros_like(_cy);_m[210:330,1200:1380]=_cy[210:330,1200:1380]
_cs,_=cv2.findContours(cv2.morphologyEx(_m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8)),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
_lago=max(_cs,key=cv2.contourArea)
water={
 "vaca":_w(_wp["vaca"][0]),
 "strip":_w(_wp["strip"][0]),
 "techo":[_w(p) for p in _wp["techo_pale"]],
 "stream":[_w(p) for p in _wp["techo_cyan"]],
 "lago":_w(cv2.approxPolyDP(_lago,2.0,True)[:,0,:].tolist()),
}
river=P([(0,455),(130,475),(250,540),(262,590),(215,690),(300,668),(350,600),(520,490),(700,350),(830,335),(905,270),(1010,230),(1020,170),(1190,180),(1420,200),(1560,235),(1650,330)])
ronda=P([(0,0),(660,0),(900,100),(960,170),(1010,230),(905,270),(830,335),(700,350),(520,490),(350,600),(300,668),(215,690),(262,590),(250,540),(130,475),(0,455)])
renov={
 "tintal":P([(1260,375),(1480,310),(1580,410),(1450,480),(1240,430)]),
 "mariapaz":P([(890,1075),(1085,910),(1150,1040),(1110,1135),(940,1120)]),
}
viv=P([(1832, 822), (1880, 838), (1978, 988), (1860, 1145), (1688, 1152), (1692, 1090), (1745, 925), (1800, 850)])
_mpb={"orange": [[[1767.9, 1142.0], [1742.6, 1140.5], [1743.1, 1131.9], [1768.4, 1133.4]], [[1721.7, 1139.2], [1695.6, 1137.6], [1696.1, 1129.0], [1722.2, 1130.5]], [[1735.6, 1140.3], [1727.0, 1139.8], [1728.6, 1113.7], [1737.2, 1114.2]], [[1777.0, 1105.0], [1776.0, 1128.0], [1781.0, 1128.0], [1782.0, 1124.0], [1776.0, 1120.0], [1776.0, 1117.0], [1778.0, 1115.0], [1782.0, 1116.0], [1782.0, 1105.0]], [[1746.0, 1101.0], [1746.0, 1107.0], [1769.0, 1108.0], [1769.0, 1103.0], [1767.0, 1107.0], [1764.0, 1107.0], [1760.0, 1102.0]], [[1736.9, 1107.9], [1711.5, 1106.3], [1712.1, 1097.7], [1737.4, 1099.3]], [[1704.7, 1124.4], [1696.1, 1123.8], [1697.7, 1097.7], [1706.3, 1098.2]], [[1861.5, 1083.9], [1856.6, 1079.0], [1874.0, 1061.6], [1878.9, 1066.5]], [[1853.0, 1072.4], [1836.6, 1056.0], [1841.5, 1051.1], [1857.9, 1067.5]], [[1883.5, 1062.9], [1866.1, 1045.5], [1871.5, 1040.1], [1888.9, 1057.5]], [[1893.0, 1053.4], [1887.6, 1048.0], [1905.0, 1030.6], [1910.4, 1036.0]], [[1894.5, 1031.9], [1877.1, 1014.5], [1882.5, 1009.1], [1899.9, 1026.5]], [[1861.0, 1023.4], [1855.6, 1018.0], [1873.0, 1000.6], [1878.4, 1006.0]], [[1934.5, 1004.8], [1920.9, 983.4], [1927.6, 979.2], [1941.2, 1000.5]], [[1945.4, 998.2], [1941.3, 991.5], [1962.7, 978.1], [1966.9, 984.7]], [[1903.5, 988.3], [1899.3, 981.6], [1920.7, 968.0], [1924.9, 974.7]], [[1953.0, 977.8], [1939.6, 956.6], [1946.2, 952.4], [1959.7, 973.5]], [[1910.8, 967.6], [1897.2, 946.5], [1903.9, 942.3], [1917.4, 963.4]], [[1922.3, 961.4], [1918.1, 954.6], [1939.6, 941.2], [1943.8, 947.9]], [[1879.9, 951.3], [1875.6, 944.7], [1897.0, 931.0], [1901.2, 937.6]], [[1930.0, 941.1], [1916.6, 919.6], [1923.2, 915.4], [1936.6, 936.9]], [[1873.6, 938.4], [1860.0, 917.0], [1866.7, 912.8], [1880.3, 934.1]], [[1835.0, 924.7], [1821.4, 919.2], [1824.2, 912.2], [1837.8, 917.6]], [[1877.2, 915.1], [1872.8, 908.6], [1893.9, 894.5], [1898.2, 901.0]], [[1912.6, 913.4], [1898.9, 892.1], [1905.5, 887.8], [1919.2, 909.2]], [[1845.3, 896.9], [1832.0, 891.2], [1835.0, 884.2], [1848.3, 889.9]]], "yellow": [[[1797.0, 1061.0], [1790.0, 1072.0], [1808.0, 1084.0], [1816.0, 1071.0], [1803.0, 1063.0]], [[1786.0, 1057.0], [1783.0, 1058.0], [1777.0, 1070.0], [1771.0, 1078.0], [1760.0, 1074.0], [1759.0, 1078.0], [1761.0, 1079.0], [1761.0, 1084.0], [1758.0, 1085.0], [1756.0, 1083.0], [1756.0, 1086.0], [1768.0, 1090.0], [1777.0, 1078.0]], [[1729.0, 1040.0], [1718.0, 1071.0], [1731.0, 1077.0], [1734.0, 1077.0], [1746.0, 1047.0]], [[1816.0, 1026.0], [1818.0, 1028.0], [1823.0, 1029.0], [1826.0, 1032.0], [1833.0, 1033.0], [1836.0, 1037.0], [1838.0, 1037.0], [1839.0, 1035.0], [1838.0, 1032.0], [1820.0, 1026.0]], [[1824.0, 1009.0], [1820.0, 1017.0], [1821.0, 1020.0], [1826.0, 1020.0], [1829.0, 1022.0], [1829.0, 1024.0], [1832.0, 1022.0], [1834.0, 1025.0], [1836.0, 1024.0], [1840.0, 1027.0], [1844.0, 1026.0], [1849.0, 1017.0], [1848.0, 1014.0], [1839.0, 1010.0], [1833.0, 1019.0]], [[1751.0, 1010.0], [1751.0, 1012.0], [1759.0, 1014.0], [1766.0, 1000.0], [1768.0, 999.0], [1783.0, 1007.0], [1776.0, 1024.0], [1784.0, 1024.0], [1786.0, 1022.0], [1796.0, 1019.0], [1800.0, 1019.0], [1801.0, 1024.0], [1803.0, 1018.0], [1809.0, 1019.0], [1815.0, 1009.0], [1816.0, 1003.0], [1807.0, 1000.0], [1800.0, 1008.0], [1790.0, 1003.0], [1796.0, 993.0], [1767.0, 978.0]], [[1792.0, 930.0], [1776.0, 963.0], [1827.0, 991.0], [1830.0, 991.0], [1847.0, 955.0]]], "blue": [[[1836.0, 879.0], [1819.0, 875.0], [1799.0, 917.0], [1801.0, 920.0], [1811.0, 926.0], [1814.0, 926.0], [1818.0, 919.0], [1822.0, 919.0], [1825.0, 912.0], [1840.0, 918.0], [1846.0, 899.0], [1832.0, 892.0], [1834.0, 886.0], [1837.0, 883.0]]]}
mpbav={k:[P([tuple(p) for p in q]) for q in v] for k,v in _mpb.items()}

# interventions: id,type,name,pos,r(m),start,end
I=[
 ("plaza_cora","plaza","Plazas satélite · Corabastos",(945,1180),230,0,6),
 ("parque_vaca","parque","Parque inundable · Humedal La Vaca",(1060,1195),210,2,9),
 ("custodia_1","custodia","Círculo de custodia multiespecie",(1035,1228),70,4,9),
 ("habitat_1","habitat","Círculo de hábitat",(1042,1158),60,4,9),
 ("saberes_1","saberes","Círculo de saberes",(955,1308),60,5,10),
 ("ecocirc","ecocirc","Puntos de economía circular",(1000,1262),100,1,5),
 ("ecotono_s","ecotono","Ecotono · borde Corabastos",(978,1300),130,3,8),
 ("cra86","corredor","Corredor verde · Av. Carrera 86",None,0,5,13),
 ("calle6","corredor","Corredor verde · Av. Calle 6",None,0,3,10),
 ("puente_c","puente","Puente verde paso de fauna · Techo",(1195,765),160,6,12),
 ("ecotono_techo","ecotono","Ecotono · Humedal de Techo",(1455,705),80,7,12),
 ("custodia_2","custodia","Círculo de custodia · Techo",(1525,782),55,8,13),
 ("ecotono_dos","ecotono","Ecotono · Las Dos Avenidas",(1418,1082),80,8,13),
 ("ecotono_ck","ecotono","Ecotono · Ciudad Kennedy",(1745,1365),90,12,18),
 ("puente_w","puente","Puente verde paso de fauna · Osorio",(300,635),100,10,15),
 ("plaza_osorio","plaza","Plazas satélite · Osorio XII",(295,750),150,10,15),
 ("centro_inv","centro","Centro de investigación, transformación y acopio",(820,250),170,12,18),
 ("plaza_bav","plaza","Plazas satélite · Bavaria",(1780,880),110,12,17),
 ("parque_bav","parque","Parque inundable · Zona Bavaria",(1760,1050),170,12,18),
 ("viv_bav","vivienda","Vivienda nueva · Zona Bavaria",(1800,985),290,12,20),
 ("habitat_2","habitat","Círculo de hábitat · Bavaria",(1840,852),55,13,18),
 ("reno_mp","renov","Renovación cohabitabilidad · María Paz",(1020,1015),0,10,20),
 ("reno_ti","renov","Renovación cohabitabilidad · El Tintal IV",(1380,410),0,14,20),
]
inter=[]
for id_,t,n,pos,r,s,e in I:
    if pos: x,y=disp(*pos)
    else:
        pts=np.array(lines[id_]); x,y=pts.mean(axis=0)
    inter.append(dict(id=id_,type=t,name=n,x=float(x),y=float(y),r=r,s=s,e=e))

# distance helpers
def samples(pts,step=60):
    pts=np.array(pts); out=[]
    for a,b in zip(pts[:-1],pts[1:]):
        L=np.hypot(*(b-a)); k=max(2,int(L/step))
        for t in np.linspace(0,1,k,endpoint=False): out.append(a+(b-a)*t)
    out.append(pts[-1]); return np.array(out)
def dmin(S): 
    S=np.array(S); dx=GX[...,None]-S[:,0]; dy=GY[...,None]-S[:,1]
    return np.sqrt(dx*dx+dy*dy).min(axis=-1)
CORA=np.array(disp(945,1180))
dCor=np.hypot(GX-CORA[0],GY-CORA[1])
# parques reales (EPSG:4686) y drenaje real como anclas verdes
from scipy.spatial import cKDTree
from shapely.geometry import shape as shp, LineString
pk=json.load(open("/tmp/claude-0/-home-claude/cfc7817e-714b-5710-ba68-4b14d8c3b130/scratchpad/in3/PARQUES.geojson"))
parks=[];gpts=[]
for f in pk["features"]:
    g=shp(f["geometry"])
    for poly in (g.geoms if g.geom_type=="MultiPolygon" else [g]):
        ring=np.array([((x-LON0)*KX,(y-LAT0)*KY) for x,y in poly.exterior.coords])
        P=Polygon(ring)
        if not P.is_valid: P=P.buffer(0)
        if P.is_empty or P.area<250: continue
        Ps=P.simplify(3)
        if Ps.geom_type!="Polygon": continue
        parks.append(dict(a=round(Ps.area),r=[[round(x),round(y)] for x,y in Ps.exterior.coords]))
        if Ps.area>1500:
            gpts.extend([list(c) for c in Ps.exterior.coords][::3]); gpts.append([Ps.centroid.x,Ps.centroid.y])
print("parques",len(parks),"ha",sum(p["a"] for p in parks)/1e4)
drg=json.load(open("/tmp/claude-0/-home-claude/cfc7817e-714b-5710-ba68-4b14d8c3b130/scratchpad/in2/DRENAJE RIOS.geojson"))
for f in drg["features"]:
    if f["properties"]["SUBTIPO"]==503:
        for part in f["geometry"]["coordinates"]:
            gpts.extend([[(x-LON0)*KX,(y-LAT0)*KY] for x,y in part][::2])
green=np.vstack([np.array(water["vaca"]),np.array(water["strip"]),np.vstack([np.array(p) for p in water["techo"]]),np.array(gpts)])
dGreen=cKDTree(green).query(np.c_[GX.ravel(),GY.ravel()])[0].reshape(GX.shape)
dCorr=dmin(np.vstack([samples(lines["cra86"]),samples(lines["calle6"])]))
plazas=[np.array(disp(*p)) for p in [(945,1180),(295,750),(1780,880)]]
dPlaza=np.min([np.hypot(GX-p[0],GY-p[1]) for p in plazas],axis=0)

def nrm(a,m):
    v=a[m]; hi=np.percentile(v,97); out=np.clip(a/max(hi,1e-9),0,1); out[~m]=0; return out
pop=nrm(gfa,mask)
ew=nrm(np.exp(-dCor/1300)*(0.35+0.65*cov),mask)
food=nrm(pop*(1-np.exp(-dCor/1800)),mask)
conn=nrm(cov*(1-np.exp(-dGreen/900)),mask)
cohab=nrm(cov*np.exp(-dGreen/1100)*(0.4+0.6*(1-np.exp(-dCor/900))),mask)
meanfl=np.where(area>0,gfa*CS*CS/np.maximum(area,1),1)
spec=nrm(cov*(1/(0.6+meanfl/3))*np.exp(-dCorr/1000)*0.7+pop*0.3,mask)
soc=nrm(0.7*pop+0.3*cov,mask)
layers=dict(ew=ew,food=food,conn=conn,cohab=cohab,spec=spec,soc=soc)

# candidates: top need cells not covered by masterplan interventions
cov_pts=[(i["x"],i["y"],max(i["r"],200)) for i in inter if i["type"] not in ("corredor",)]
ok=mask.copy()
for x,y,r in cov_pts: ok&=np.hypot(GX-x,GY-y)>r+250
for lname in ("cra86","calle6"):
    ok&= dmin(samples(lines[lname]))>120 if False else ok
spec_def={
 "ew":("Residuos","Punto de compostaje y recolección de barrio","ecocirc"),
 "food":("Alimentos","Plaza de mercado y huerta de proximidad","plaza"),
 "conn":("Conectividad","Parque de bolsillo y corredor verde","corredor"),
 "cohab":("Cohabitabilidad","Ecotono y refugio de fauna","ecotono"),
 "spec":("Especulación","Banco de tierras y vivienda comunitaria","vivienda"),
}
cands=[]
for key,(ind,what,typ) in spec_def.items():
    sc=np.where(ok,layers[key],-1).copy(); picked=[]
    for _ in range(3):
        j=np.unravel_index(np.argmax(sc),sc.shape)
        if sc[j]<=0.2: break
        px,py=GX[j],GY[j]; picked.append((px,py,float(sc[j])))
        sc[np.hypot(GX-px,GY-py)<650]=-1
    for k,(px,py,s) in enumerate(picked):
        cands.append(dict(id=f"c_{key}_{k}",key=key,ind=ind,what=what,type=typ,x=float(px),y=float(py),score=round(s,2),
                          s=[6,10,14][k]))
print("candidates",len(cands))


# drenaje real (EPSG:4686 ~ WGS84)
dr=json.load(open("/tmp/claude-0/-home-claude/cfc7817e-714b-5710-ba68-4b14d8c3b130/scratchpad/in2/DRENAJE RIOS.geojson"))
rivers=[]
for f in dr["features"]:
    for part in f["geometry"]["coordinates"]:
        pts=np.array([((p[0]-LON0)*KX,(p[1]-LAT0)*KY) for p in part])
        # simplificar a ~8 m
        from shapely.geometry import LineString
        ls=LineString(pts).simplify(8)
        rivers.append(dict(name=f["properties"]["NOMBRE"],t=int(f["properties"]["SUBTIPO"]),pts=[[round(x,1),round(y,1)] for x,y in ls.coords]))

# vías reales
vd=json.load(open("/tmp/claude-0/-home-claude/cfc7817e-714b-5710-ba68-4b14d8c3b130/scratchpad/in4/vias.geojson"))
rbuf=rect.buffer(250)
cls={0:[],1:[],2:[]}
for f in vd["features"]:
    p=f["properties"]; t=p["MVITIPO"]
    c=2 if (t in("AK","AC") or p["MVINOMBRE"]) else 1 if t in("DG","TV") else 0
    for part in f["geometry"]["coordinates"]:
        ls=LineString([((x-LON0)*KX,(y-LAT0)*KY) for x,y in part])
        if not ls.intersects(rbuf): continue
        ls=ls.simplify(4)
        if ls.length<15: continue
        cls[c].append(np.array(ls.coords))
roads={}
for c,L in cls.items():
    co=np.concatenate([np.round(a*2) for a in L]).astype(np.int16) if L else np.zeros((0,2),np.int16)
    ln=np.array([len(a) for a in L],dtype=np.uint16)
    roads[str(c)]=dict(n=int(len(L)),xy=base64.b64encode(co.astype(np.int16).tobytes()).decode(),len=base64.b64encode(ln.tobytes()).decode())
    print("vias clase",c,len(L),"tramos",len(co),"pts")

q8=lambda a:base64.b64encode(np.clip(np.round(a*255),0,255).astype(np.uint8).tobytes()).decode()
def b64(a,dt): return base64.b64encode(a.astype(dt).tobytes()).decode()
tr=json.load(open("/tmp/claude-0/-home-claude/cfc7817e-714b-5710-ba68-4b14d8c3b130/scratchpad/in5/ARBOLADO URBANO.geojson"))
tx=[];ty=[];th=[]
for f in tr["features"]:
    if f["geometry"]["type"]!="Point": continue
    lo,la=f["geometry"]["coordinates"][:2]
    x=(lo-LON0)*KX; y=(la-LAT0)*KY
    ix=int((x-X0)/CS); iy=int((y-Y0)/CS)
    if 0<=ix<nx and 0<=iy<ny and mask[iy,ix]:
        h=f["properties"].get("Altura_Tot") or 4
        tx.append(x);ty.append(y);th.append(min(max(h,1),30))
tx=np.array(tx);ty=np.array(ty);th=np.array(th)
print("arboles en el poligono",len(tx),"altura media",th.mean())
_ov=json.load(open('/home/claude/sim/bav_override.json'));viv=_ov['viv'];mpbav=_ov['mpbav']
for _o in inter:
    if _o['id'] in _ov['inter']:_o['x'],_o['y']=_ov['inter'][_o['id']]
out=dict(
 trees=dict(n=int(len(tx)),x=b64(np.round(tx*2),np.int16),y=b64(np.round(ty*2),np.int16),h=b64(np.round(th*4),np.uint8)),
 grid=dict(x0=X0,y0=Y0,cs=CS,nx=nx,ny=ny,mask=b64(mask.astype(np.uint8),np.uint8),cov=q8(cov),pop=q8(pop),
           ew=q8(ew),food=q8(food),conn=q8(conn),cohab=q8(cohab),spec=q8(spec),soc=q8(soc),
           dcor=b64(np.clip(dCor/20,0,65535),np.uint16)),
 rect=rect_pts,
 b=dict(n=int(N),x=b64(np.round(bx*2),np.int16),y=b64(np.round(by*2),np.int16),w=b64(np.round(bw*2),np.uint16),
        d=b64(np.round(bd*2),np.uint16),a=b64(np.round(ba/math.pi*255),np.uint8),f=b64(bf,np.uint8)),
 rivers=rivers,parks=parks,roads=roads,lines=lines,water=water,river=river,ronda=ronda,renov=renov,viv=viv,mpbav=mpbav,inter=inter,cands=cands,
 cora=[float(CORA[0]),float(CORA[1])],
 stats=dict(buildings=int(N),floors_mean=float(np.average(bf,weights=barea)),area_ha=float(barea.sum()/1e4)),
)
json.dump(out,open("/home/claude/sim/data.json","w"),separators=(",",":"))
import os; print(os.path.getsize("/home/claude/sim/data.json")/1e6,"MB", out["stats"])
for c in cands: print(c["key"],round(c["x"]),round(c["y"]),c["score"])
