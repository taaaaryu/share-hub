"use client";

import { useMemo, useRef, useState } from "react";

type AimAnalysisView = any; type AimEventView = any; type DamagePoint = any;

export type VideoPreview = {
  url: string;
  content_type: string;
  filename: string;
};

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function formatTimestamp(timestampSec: number) {
  const totalCentiseconds = Math.max(0, Math.round(timestampSec * 100));
  const minutes = Math.floor(totalCentiseconds / 6000);
  const seconds = Math.floor((totalCentiseconds % 6000) / 100);
  const centiseconds = totalCentiseconds % 100;
  return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}.${centiseconds.toString().padStart(2, "0")}`;
}

const AIM_SCATTER_SCALE = 2.4;

function directionLabel(x: number, y: number) {
  const horizontal = Math.abs(x) < 5 ? "" : x > 0 ? "右" : "左";
  const vertical = Math.abs(y) < 5 ? "" : y > 0 ? "下" : "上";
  return horizontal || vertical ? `${vertical}${horizontal}寄り` : "ほぼ中央";
}

function nearestAimEvent(events: AimEventView[], currentTime: number) {
  let nearest: AimEventView | null = null;
  let nearestDelta = Number.POSITIVE_INFINITY;
  for (const event of events) {
    const delta = Math.abs(event.timestampSec - currentTime);
    if (delta < nearestDelta) {
      nearest = event;
      nearestDelta = delta;
    }
  }
  return nearestDelta <= 0.12 ? nearest : null;
}

export function AimAnalysisPanel({
  preview,
  aim,
  damageTimeline,
  durationSec,
}: {
  preview: VideoPreview | null;
  aim: AimAnalysisView | null;
  damageTimeline: DamagePoint[];
  durationSec: number;
}) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [mediaDuration, setMediaDuration] = useState(durationSec);
  const activeEvent = useMemo(
    () => aim ? nearestAimEvent(aim.events, currentTime) : null,
    [aim, currentTime],
  );

  const seekToTime = (timestampSec: number) => {
    const video = videoRef.current;
    if (video) {
      const seek = () => {
        video.currentTime = timestampSec;
        video.pause();
      };
      if (video.readyState === 0) video.addEventListener("loadedmetadata", seek, { once: true });
      else seek();
    }
    setCurrentTime(timestampSec);
  };

  const maxTime = Math.max(mediaDuration, durationSec, damageTimeline.at(-1)?.timestampSec ?? 0, 0.01);
  const hitPoints = damageTimeline.filter((point) => point.damage > 0);
  const totalDamage = hitPoints.reduce((total, point) => total + point.damage, 0);
  const activeDamagePoint = hitPoints.reduce<DamagePoint | null>((nearest, point) => {
    if (!nearest || Math.abs(point.timestampSec - currentTime) < Math.abs(nearest.timestampSec - currentTime)) return point;
    return nearest;
  }, null);
  const activeDamageDelta = activeDamagePoint ? Math.abs(activeDamagePoint.timestampSec - currentTime) : Number.POSITIVE_INFINITY;
  let runningDamage = 0;
  let previousGraphY = 205;
  const stepPolylineParts = ["0,205"];
  const graphPoints = hitPoints.map((point) => {
    const x = clamp((point.timestampSec / maxTime) * 100, 0, 100);
    stepPolylineParts.push(`${x * 10},${previousGraphY}`);
    runningDamage += point.damage;
    const y = 205 - (runningDamage / Math.max(1, totalDamage)) * 167;
    stepPolylineParts.push(`${x * 10},${y}`);
    previousGraphY = y;
    return { ...point, cumulativeDamage: runningDamage, x, y: 17 + (1 - runningDamage / Math.max(1, totalDamage)) * 68 };
  });
  stepPolylineParts.push(`1000,${previousGraphY}`);
  const stepPolyline = stepPolylineParts.join(" ");
  const currentMarker = clamp((currentTime / maxTime) * 100, 0, 100);
  const currentDamage = graphPoints.reduce(
    (damage, point) => point.timestampSec <= currentTime ? point.cumulativeDamage : damage,
    0,
  );

  return (
    <section className="score-card aim-card">
      <div className="aim-heading">
        <div><p className="section-kicker">VIDEO & AIM TRACE</p><h2>照準と敵位置のずれ</h2></div>
        {aim ? <span>{aim.matchedShotCount} SHOTS</span> : null}
      </div>
      {preview ? (
        <div
          className="aim-video-stage"
          style={aim ? { aspectRatio: `${aim.videoWidth} / ${aim.videoHeight}` } : undefined}
        >
          <video
            ref={videoRef}
            controls
            playsInline
            preload="metadata"
            aria-label={`${preview.filename}の解析対象動画`}
            onTimeUpdate={(event) => setCurrentTime(event.currentTarget.currentTime)}
            onSeeked={(event) => setCurrentTime(event.currentTarget.currentTime)}
            onLoadedMetadata={(event) => {
              const nextDuration = event.currentTarget.duration;
              if (Number.isFinite(nextDuration) && nextDuration > 0) setMediaDuration(nextDuration);
            }}
          >
            <source src={preview.url} type={preview.content_type} />
            お使いのブラウザは動画プレビューに対応していません。
          </video>
          {aim ? <span className="aim-crosshair" aria-hidden="true"><i /><b /></span> : null}
          {activeEvent && aim ? (
            <svg
              className="aim-overlay"
              viewBox={`0 0 ${aim.videoWidth} ${aim.videoHeight}`}
              preserveAspectRatio="none"
              aria-label={`射撃時の敵位置。照準から${Math.round(activeEvent.errorPx)}ピクセルのずれ`}
            >
              {aim.roiBbox ? <rect className="aim-roi aim-inference-roi" x={aim.roiBbox[0]} y={aim.roiBbox[1]} width={aim.roiBbox[2] - aim.roiBbox[0]} height={aim.roiBbox[3] - aim.roiBbox[1]} /> : null}
              <rect
                x={activeEvent.bbox[0]}
                y={activeEvent.bbox[1]}
                width={activeEvent.bbox[2] - activeEvent.bbox[0]}
                height={activeEvent.bbox[3] - activeEvent.bbox[1]}
              />
            </svg>
          ) : aim?.roiBbox ? <svg className="aim-overlay" viewBox={`0 0 ${aim.videoWidth} ${aim.videoHeight}`} preserveAspectRatio="none" aria-label="敵推論ROI"><rect className="aim-roi aim-inference-roi" x={aim.roiBbox[0]} y={aim.roiBbox[1]} width={aim.roiBbox[2] - aim.roiBbox[0]} height={aim.roiBbox[3] - aim.roiBbox[1]} /></svg> : null}
        </div>
      ) : <p className="aim-empty">この結果では動画のプレビューURLを取得できませんでした。</p>}
      <div className="damage-timeline damage-video-timeline" aria-label="動画に連動する累積ダメージとヒット履歴">
        <div className="damage-timeline-heading">
          <div><span className="section-kicker">DAMAGE PROGRESSION</span><h3>時間とダメージの推移</h3></div>
          <div className="damage-total"><span>CURRENT / TOTAL</span><strong>{hitPoints.length ? <>{currentDamage}<small> / {totalDamage}</small></> : "未取得"}</strong></div>
        </div>
        {hitPoints.length > 0 ? <>
          <div className="damage-graph-wrap">
            <button
              type="button"
              className="damage-chart-seek"
              aria-label="グラフ上の時刻へ動画を移動"
              onClick={(event) => {
                const bounds = event.currentTarget.getBoundingClientRect();
                seekToTime(clamp((event.clientX - bounds.left) / bounds.width, 0, 1) * maxTime);
              }}
            />
            <span className="damage-y-label damage-y-max">{totalDamage}</span>
            <span className="damage-y-label damage-y-zero">0</span>
            <svg className="damage-graph" viewBox="0 0 1000 220" role="img" aria-label={`動画時間に対する累積ダメージ。合計${totalDamage}ダメージ`} preserveAspectRatio="none">
              <polygon points={`0,220 ${stepPolyline} 1000,220`} className="damage-step-area" />
              <polyline points={stepPolyline} className="damage-step-line" />
              <line x1={currentMarker * 10} x2={currentMarker * 10} y1="0" y2="220" className="damage-current-line" />
            </svg>
            <span className="damage-current-time" style={{ left: `${clamp(currentMarker, 6, 94)}%` }}>{formatTimestamp(currentTime)}</span>
            {graphPoints.map((point, index) => <button
              key={`${point.frameNumber}-${index}`}
              className={`damage-step-point${activeDamageDelta <= 0.35 && activeDamagePoint?.frameNumber === point.frameNumber && activeDamagePoint.timestampSec === point.timestampSec && activeDamagePoint.damage === point.damage ? " active" : ""}`}
              style={{ left: `${point.x}%`, top: `${point.y}%` }}
              type="button"
              aria-label={`${formatTimestamp(point.timestampSec)}、${point.damage}ダメージ、累積${point.cumulativeDamage}ダメージへ移動`}
              onClick={() => seekToTime(point.timestampSec)}
            ><span>{point.cumulativeDamage}</span></button>)}
          </div>
          <div className="damage-timeline-axis"><span>{formatTimestamp(0)}</span><span>{formatTimestamp(maxTime / 2)}</span><span>{formatTimestamp(maxTime)}</span></div>
          <div className="damage-hit-heading"><span>HIT TIMELINE</span><b>{hitPoints.length} HITS</b></div>
          <div className="damage-hit-list">
            {graphPoints.map((point, index) => <button
              key={`hit-${point.frameNumber}-${index}`}
              type="button"
              className={activeDamageDelta <= 0.35 && activeDamagePoint?.frameNumber === point.frameNumber && activeDamagePoint.timestampSec === point.timestampSec && activeDamagePoint.damage === point.damage ? "active" : ""}
              aria-label={`${formatTimestamp(point.timestampSec)}、${point.damage}ダメージへ移動`}
              onClick={() => seekToTime(point.timestampSec)}
            >
              <span>{formatTimestamp(point.timestampSec)}</span>
              <strong>+{point.damage}</strong>
              <small>累積 {point.cumulativeDamage}</small>
            </button>)}
          </div>
        </> : <p className="damage-empty">表示できるダメージ時刻がありません。</p>}
      </div>
      {aim ? (
        <>
          <div className="aim-summary-grid">
            <div><span>平均ずれ</span><strong>{aim.averageErrorPx.toFixed(1)}<small> px</small></strong></div>
            <div><span>ずれ傾向</span><strong className="aim-direction">{directionLabel(aim.averageOffsetX, aim.averageOffsetY)}</strong></div>
          </div>
          <div className="aim-scatter-wrap">
            <div className="aim-scatter" aria-label="射撃時の敵中心位置分布">
              <span className="aim-scatter-cross" aria-hidden="true" />
              {aim.events.map((event) => (
                <button
                  type="button"
                  key={`${event.frameNumber}-${event.enemyFrameNumber}`}
                  className="aim-point"
                  style={{
                    left: `${clamp(50 + (event.offsetX / aim.videoWidth) * 100 * AIM_SCATTER_SCALE, 2, 98)}%`,
                    top: `${clamp(50 + (event.offsetY / aim.videoHeight) * 100 * AIM_SCATTER_SCALE, 2, 98)}%`,
                    opacity: clamp(event.confidence, 0.35, 1),
                  }}
                  aria-label={`${event.timestampSec.toFixed(2)}秒へ移動。ずれ${Math.round(event.errorPx)}ピクセル`}
                  onClick={() => seekToTime(event.timestampSec)}
                />
              ))}
            </div>
            <p>点を選ぶと、その射撃時刻へ動画を移動します。中央が射撃時の照準、各点が検出した敵bboxの中心です。</p>
          </div>
        </>
      ) : (
        <p className="aim-empty">この解析結果には敵bboxがまだ含まれていません。動画プレビューのみ表示しています。</p>
      )}
    </section>
  );
}
