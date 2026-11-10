#!/usr/bin/env python3
"""Generate the two figures used by this deck (aggregates only, no game imagery)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent
INK="#161616"; SUB="#525252"; BLUE="#0f62fe"; LBLUE="#d0e2ff"; TEAL="#007d79"
RED="#da1e28"; GRAY="#8d8d8d"; DGRAY="#393939"; PALE="#f4f4f4"
plt.rcParams["font.family"]=["Hiragino Sans","Hiragino Sans GB","Arial Unicode MS"]

# ---- Figure 1: threshold fires on two training-range clips ----
clips=["クリップ1 (23.6秒)","クリップ2 (24.4秒)"]
bursts=[73,288]; settled=[30,37]; moving=[43,251]; sigs=[29,36]
fig,axes=plt.subplots(1,2,figsize=(7.2,4.3),dpi=200)
for ax,title,vals in zip(axes,clips,[(bursts[0],settled[0],moving[0],sigs[0]),(bursts[1],settled[1],moving[1],sigs[1])]):
    b,s,m,g=vals
    labels=["しきい値を\n超えた回数","うち\nすぐ止まった","うち\n動き続けた","止まった\n見た目の種類"]
    colors=[DGRAY,TEAL,RED,BLUE]
    bars=ax.bar(range(4),[b,s,m,g],color=colors,width=0.62)
    for i,(bar,v) in enumerate(zip(bars,[b,s,m,g])):
        ax.text(bar.get_x()+bar.get_width()/2,v+max(vals)*0.03,f"{v}",ha="center",va="bottom",fontsize=13,fontweight="bold",color=INK)
    ax.set_title(title,fontsize=12,color=INK,pad=10)
    ax.set_xticks(range(4)); ax.set_xticklabels(labels,fontsize=8.5,color=SUB)
    ax.set_ylim(0,max(vals)*1.22); ax.set_yticks([])
    for sp in ["top","right","left"]: ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRAY)
fig.suptitle("同じ「変化した」でも、中身は3種類に分かれる",fontsize=14,fontweight="bold",color=INK,y=0.98)
fig.text(0.5,0.015,"計測: 1280x720 / 約60fps の訓練場クリップ2本。右上ダメージROIだけを対象に、グレー190しきい値＋変化率1.5%で数えた。",ha="center",fontsize=7.5,color=SUB)
fig.tight_layout(rect=[0,0.04,1,0.93])
fig.savefig(ROOT/"threshold_split.png",facecolor="white")
plt.close(fig)

# ---- Figure 2: plan ladder ----
fig,ax=plt.subplots(figsize=(7.2,4.6),dpi=200)
ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis("off")
steps=[
 ("1","素材と正解を固定","TAA-43 / 人が必要","どのクリップのどのフレームが\n本当の数字変化かを人が付ける",PALE,INK),
 ("2","3方式を同じ素材で比較","TAA-45 / 今日ここまで準備","A=現行の二値差分\nB=局所コントラスト+文字マスク\nC=B+周辺の背景変化量",LBLUE,INK),
 ("3","採用は1方式だけ","TAA-46 / 時系列で確定","変化中の連打を抑え、\n確定した見た目だけをOCRへ",PALE,INK),
 ("4","段階ONと実費確認","TAA-47・TAA-49・TAA-50","shadow→限定ON。\n精度が落ちたら即OFF",PALE,INK),
]
y=93
for num,title,owner,body,color,ink in steps:
    box=FancyBboxPatch((8,y-15.6),84,14.8,boxstyle="round,pad=0.9,rounding_size=1.2",
                       linewidth=1.2,edgecolor=GRAY,facecolor=color)
    ax.add_patch(box)
    ax.text(4.5,y-7.5,num,fontsize=15,fontweight="bold",color=BLUE,ha="center",va="center")
    ax.text(10.5,y-4.4,title,fontsize=11.2,fontweight="bold",color=INK,va="center")
    ax.text(10.5,y-7.2,body,fontsize=7.4,color=SUB,va="top",linespacing=1.4)
    ax.text(90,y-4.4,owner,fontsize=8.0,color=TEAL,ha="right",va="center",fontweight="bold")
    if y>40:
        ax.add_patch(FancyArrowPatch((50,y-16.0),(50,y-19.4),arrowstyle="-|>",mutation_scale=12,color=GRAY,linewidth=1.4))
    y-=21.5
ax.text(50,3,"今日できたのは 2 の手前の計測まで。1 の正解ラベルが無いと精度は出せない。",fontsize=8.5,color=INK,ha="center",fontweight="bold")
fig.tight_layout()
fig.savefig(ROOT/"plan_ladder.png",facecolor="white")
plt.close(fig)
print("ok")
