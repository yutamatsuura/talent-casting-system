"use client"

import { useState, useRef } from "react"
import {
  X,
  TrendingUp,
  Users,
  DollarSign,
  Lock,
  Unlock,
  Star,
  Award,
  Target,
  ChevronLeft,
  ChevronRight,
  Calendar,
  Heart,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import type { Talent } from "@/lib/talent-data"

type TalentDetailModalProps = {
  talent: Talent
  isOpen: boolean
  onClose: () => void
}

function getScoreColor(score: number): string {
  if (score >= 90) return "bg-emerald-500"
  if (score >= 75) return "bg-blue-500"
  if (score >= 60) return "bg-amber-500"
  return "bg-gray-400"
}

function getScoreTextColor(score: number): string {
  if (score >= 90) return "text-emerald-600"
  if (score >= 75) return "text-blue-600"
  if (score >= 60) return "text-amber-600"
  return "text-gray-600"
}

function getScoreBgColor(score: number): string {
  if (score >= 90) return "from-emerald-50 to-emerald-100/50"
  if (score >= 75) return "from-blue-50 to-blue-100/50"
  if (score >= 60) return "from-amber-50 to-amber-100/50"
  return "from-gray-50 to-gray-100/50"
}

export function TalentDetailModal({ talent, isOpen, onClose }: TalentDetailModalProps) {
  const [isMasked, setIsMasked] = useState(true)
  const timelineRef = useRef<HTMLDivElement>(null)

  if (!isOpen) return null

  const detailData = talent.detailData

  const scrollTimeline = (direction: "left" | "right") => {
    if (timelineRef.current) {
      const scrollAmount = 344
      const newScrollLeft = timelineRef.current.scrollLeft + (direction === "right" ? scrollAmount : -scrollAmount)
      timelineRef.current.scrollTo({
        left: newScrollLeft,
        behavior: "smooth",
      })
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="relative w-full max-w-6xl max-h-[90vh] bg-gray-50 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="sticky top-0 z-10 bg-white border-b border-gray-200 p-6 shadow-sm">
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-4 right-4 hover:bg-gray-100 rounded-full"
            onClick={onClose}
          >
            <X className="h-5 w-5" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            className="absolute top-4 right-16 flex items-center gap-2 px-4 border-gray-300 bg-transparent"
            onClick={() => setIsMasked(!isMasked)}
          >
            {isMasked ? (
              <>
                <Lock className="h-4 w-4" />
                <span className="text-sm font-medium">詳細を表示</span>
              </>
            ) : (
              <>
                <Unlock className="h-4 w-4" />
                <span className="text-sm font-medium">詳細を非表示</span>
              </>
            )}
          </Button>

          <div className="flex items-start gap-6">
            {/* Talent Photo */}
            <div
              className="w-24 h-24 rounded-xl flex-shrink-0 shadow-md ring-2 ring-gray-200"
              style={{
                backgroundImage: `url(${talent.imageUrl})`,
                backgroundSize: "cover",
                backgroundPosition: "center",
              }}
            />

            {/* Talent Info - Middle Section */}
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl font-bold text-gray-900">{talent.name}</h2>
                <span className="text-sm text-gray-500">({talent.kana})</span>
              </div>
              <div className="flex items-center gap-3 text-sm mb-3">
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full font-medium">{talent.category}</span>
                {talent.age && <span className="text-gray-600">{talent.age}歳</span>}
              </div>
              {talent.introduction && <p className="text-sm text-gray-600 leading-relaxed">{talent.introduction}</p>}
            </div>

            <div className="flex-shrink-0">
              <div className="inline-flex items-center gap-3 bg-gradient-to-r from-blue-50 to-indigo-50 px-5 py-3 rounded-xl border border-blue-200">
                <Star className="h-6 w-6 fill-blue-500 text-blue-500" />
                <div>
                  <div className="text-3xl font-bold text-blue-600">{talent.matchScore}%</div>
                  <div className="text-xs text-gray-600 font-medium">マッチング度</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-180px)] p-6 space-y-6">
          {/* Score Breakdown */}
          {detailData?.scoreBreakdown && (
            <section>
              <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-blue-600" />
                スコア詳細分析
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Target Fit */}
                <div
                  className={`bg-gradient-to-br ${getScoreBgColor(detailData.scoreBreakdown.targetFit.score)} rounded-xl p-5 shadow-sm border border-gray-200`}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <div className="p-2 bg-white rounded-lg shadow-sm">
                      <Target className="h-4 w-4 text-blue-600" />
                    </div>
                    <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">ターゲット層</span>
                  </div>
                  <div className="mb-2">
                    <div
                      className={`text-4xl font-bold ${getScoreTextColor(detailData.scoreBreakdown.targetFit.score)}`}
                    >
                      {isMasked ? "🔒" : detailData.scoreBreakdown.targetFit.score}
                    </div>
                    <div className="text-xs text-gray-500 font-medium mt-1">/ 100点</div>
                  </div>
                  <div className="w-full h-2 bg-white/50 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${isMasked ? "bg-gray-400" : getScoreColor(detailData.scoreBreakdown.targetFit.score)} transition-all duration-500`}
                      style={{ width: isMasked ? "100%" : `${detailData.scoreBreakdown.targetFit.score}%` }}
                    />
                  </div>
                  {detailData.scoreBreakdown.targetFit.f1 && !isMasked && (
                    <div className="mt-3 pt-3 border-t border-gray-200 space-y-1.5">
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-600">F1層 好感度</span>
                        <span className="font-bold text-blue-600">
                          {detailData.scoreBreakdown.targetFit.f1.favorability}%
                        </span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-600">F1層 認知度</span>
                        <span className="font-bold text-blue-600">
                          {detailData.scoreBreakdown.targetFit.f1.recognition}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Industry Experience */}
                <div
                  className={`bg-gradient-to-br ${getScoreBgColor(detailData.scoreBreakdown.industryExp.score)} rounded-xl p-5 shadow-sm border border-gray-200`}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <div className="p-2 bg-white rounded-lg shadow-sm">
                      <Award className="h-4 w-4 text-emerald-600" />
                    </div>
                    <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">業界経験</span>
                  </div>
                  <div className="mb-2">
                    <div
                      className={`text-4xl font-bold ${getScoreTextColor(detailData.scoreBreakdown.industryExp.score)}`}
                    >
                      {isMasked ? "🔒" : detailData.scoreBreakdown.industryExp.score}
                    </div>
                    <div className="text-xs text-gray-500 font-medium mt-1">/ 100点</div>
                  </div>
                  <div className="w-full h-2 bg-white/50 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${isMasked ? "bg-gray-400" : getScoreColor(detailData.scoreBreakdown.industryExp.score)} transition-all duration-500`}
                      style={{ width: isMasked ? "100%" : `${detailData.scoreBreakdown.industryExp.score}%` }}
                    />
                  </div>
                </div>

                {/* Brand Affinity */}
                <div
                  className={`bg-gradient-to-br ${getScoreBgColor(detailData.scoreBreakdown.brandAffinity.score)} rounded-xl p-5 shadow-sm border border-gray-200`}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <div className="p-2 bg-white rounded-lg shadow-sm">
                      <Heart className="h-4 w-4 text-pink-600" />
                    </div>
                    <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">ブランド親和性</span>
                  </div>
                  <div className="mb-2">
                    <div
                      className={`text-4xl font-bold ${getScoreTextColor(detailData.scoreBreakdown.brandAffinity.score)}`}
                    >
                      {isMasked ? "🔒" : detailData.scoreBreakdown.brandAffinity.score}
                    </div>
                    <div className="text-xs text-gray-500 font-medium mt-1">/ 100点</div>
                  </div>
                  <div className="w-full h-2 bg-white/50 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${isMasked ? "bg-gray-400" : getScoreColor(detailData.scoreBreakdown.brandAffinity.score)} transition-all duration-500`}
                      style={{ width: isMasked ? "100%" : `${detailData.scoreBreakdown.brandAffinity.score}%` }}
                    />
                  </div>
                </div>

                {/* Cost Efficiency */}
                <div
                  className={`bg-gradient-to-br ${getScoreBgColor(detailData.scoreBreakdown.costEff.score)} rounded-xl p-5 shadow-sm border border-gray-200`}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <div className="p-2 bg-white rounded-lg shadow-sm">
                      <DollarSign className="h-4 w-4 text-amber-600" />
                    </div>
                    <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">コスト効率</span>
                  </div>
                  <div className="mb-2">
                    <div className={`text-4xl font-bold ${getScoreTextColor(detailData.scoreBreakdown.costEff.score)}`}>
                      {isMasked ? "🔒" : detailData.scoreBreakdown.costEff.score}
                    </div>
                    <div className="text-xs text-gray-500 font-medium mt-1">/ 100点</div>
                  </div>
                  <div className="w-full h-2 bg-white/50 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${isMasked ? "bg-gray-400" : getScoreColor(detailData.scoreBreakdown.costEff.score)} transition-all duration-500`}
                      style={{ width: isMasked ? "100%" : `${detailData.scoreBreakdown.costEff.score}%` }}
                    />
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* CM History - Horizontal Timeline */}
          {detailData?.cmHistory && detailData.cmHistory.length > 0 && (
            <section className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-xl font-bold flex items-center gap-2 text-gray-800">
                  <div className="p-2 bg-indigo-100 rounded-lg">
                    <Users className="h-5 w-5 text-indigo-600" />
                  </div>
                  CM出演履歴タイムライン
                </h3>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-8 w-8 rounded-full bg-transparent"
                    onClick={() => scrollTimeline("left")}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-8 w-8 rounded-full bg-transparent"
                    onClick={() => scrollTimeline("right")}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="relative">
                <div
                  ref={timelineRef}
                  className="overflow-x-auto overflow-y-visible pb-4 scrollbar-thin scrollbar-thumb-indigo-300 scrollbar-track-gray-100"
                  style={{
                    scrollbarWidth: "thin",
                    scrollbarColor: "#a5b4fc #f3f4f6",
                  }}
                >
                  <div className="flex gap-6 min-w-max px-2 py-2">
                    {detailData.cmHistory.flatMap((category) =>
                      category.items.map((item, itemIndex) => (
                        <div
                          key={`${category.category}-${itemIndex}`}
                          className="w-80 flex-shrink-0 bg-gradient-to-br from-white to-indigo-50 rounded-xl border-2 border-indigo-200 shadow-md hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 overflow-hidden group"
                        >
                          {/* Card Header with gradient */}
                          <div className="h-32 bg-gradient-to-br from-indigo-500 to-purple-600 relative overflow-hidden">
                            <div className="absolute inset-0 bg-black/20" />
                            <div className="absolute inset-0 flex items-center justify-center">
                              <div className="text-center text-white">
                                <Calendar className="h-8 w-8 mx-auto mb-2 opacity-90" />
                                <p className="text-sm font-semibold opacity-90">{item.period}</p>
                              </div>
                            </div>
                            <div className="absolute top-3 right-3">
                              <span className="px-3 py-1 bg-white/90 backdrop-blur-sm text-indigo-700 rounded-full text-xs font-bold shadow-lg">
                                {category.category}
                              </span>
                            </div>
                          </div>

                          {/* Card Body */}
                          <div className="p-5 space-y-4">
                            {/* Brand Name */}
                            <div>
                              <h4 className="font-bold text-lg text-gray-800 mb-1 line-clamp-2 group-hover:text-indigo-600 transition-colors">
                                {item.brand}
                              </h4>
                              <p className="text-xs text-gray-500">{category.category}</p>
                            </div>

                            {/* Performance Metrics */}
                            {item.results && (
                              <div className="space-y-3">
                                <div className="flex items-center gap-2 mb-2">
                                  <TrendingUp className="h-4 w-4 text-indigo-600" />
                                  <p className="text-xs font-bold text-gray-700 tracking-wide">パフォーマンス指標</p>
                                </div>

                                <div className="grid grid-cols-3 gap-2">
                                  {Object.entries(item.results)
                                    .slice(0, 3)
                                    .map(([key, value]) => {
                                      // Parse numeric value for progress bar
                                      const numericValue =
                                        typeof value === "string"
                                          ? Number.parseFloat(value.replace(/[^\d.]/g, ""))
                                          : value
                                      const maxValue =
                                        key.includes("率") || key.includes("CTR") || key.includes("CVR") ? 10 : 100
                                      const percentage = Math.min((numericValue / maxValue) * 100, 100)

                                      return (
                                        <div key={key} className="text-center">
                                          <p className="text-xs text-gray-600 mb-1 truncate">{key}</p>
                                          <p className="text-lg font-bold text-indigo-600">{isMasked ? "🔒" : value}</p>
                                          {!isMasked && (
                                            <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden mt-1">
                                              <div
                                                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
                                                style={{ width: `${percentage}%` }}
                                              />
                                            </div>
                                          )}
                                        </div>
                                      )
                                    })}
                                </div>

                                {/* ROI Display */}
                                {item.results["ROI"] && (
                                  <div className="mt-3 p-3 bg-gradient-to-r from-emerald-50 to-green-50 rounded-lg border border-emerald-200">
                                    <div className="flex items-center justify-between">
                                      <div className="flex items-center gap-2">
                                        <DollarSign className="h-4 w-4 text-emerald-600" />
                                        <span className="text-xs font-semibold text-gray-700">ROI</span>
                                      </div>
                                      <span className="text-xl font-bold text-emerald-600">
                                        {isMasked ? "🔒" : item.results["ROI"]}
                                      </span>
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}

                            {/* View Details Button */}
                            <Button
                              variant="outline"
                              size="sm"
                              className="w-full border-indigo-300 text-indigo-600 hover:bg-indigo-50 hover:border-indigo-400 transition-all bg-transparent"
                            >
                              詳細を見る →
                            </Button>
                          </div>

                          {/* Timeline connector dot */}
                          <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 w-3 h-3 bg-indigo-500 rounded-full border-2 border-white shadow-md" />
                        </div>
                      )),
                    )}
                  </div>
                </div>

                {/* Timeline line */}
                <div className="absolute -bottom-2 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-indigo-300 to-transparent" />
              </div>

              {/* Scroll indicator */}
              <div className="flex justify-center mt-6 gap-1">
                {detailData.cmHistory.map((_, index) => (
                  <div key={index} className="h-1.5 w-8 bg-indigo-200 rounded-full" />
                ))}
              </div>
            </section>
          )}

          {/* Cost Information */}
          {detailData?.cost && (
            <section className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
              <h3 className="text-xl font-bold mb-5 flex items-center gap-2 text-gray-800">
                <div className="p-2 bg-emerald-100 rounded-lg">
                  <DollarSign className="h-5 w-5 text-emerald-600" />
                </div>
                料金目安
              </h3>

              <div className="mb-8">
                <h4 className="text-lg font-bold mb-4 text-gray-700">基本料金プラン</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {detailData.cost.tvCm && (
                    <div className="p-5 bg-gradient-to-br from-emerald-50 to-white rounded-xl border border-emerald-100 shadow-sm">
                      <h4 className="font-bold text-lg mb-4 text-gray-800 flex items-center gap-2">
                        <span className="w-8 h-8 bg-emerald-600 text-white rounded-lg flex items-center justify-center text-sm">
                          TV
                        </span>
                        テレビCM
                      </h4>
                      <div className="p-3 bg-white rounded-lg border border-emerald-200">
                        <p className="text-xl font-bold text-emerald-600">
                          {isMasked ? "🔒" : detailData.cost.tvCm.range}
                        </p>
                      </div>
                    </div>
                  )}

                  {detailData.cost.webCm && (
                    <div className="p-5 bg-gradient-to-br from-blue-50 to-white rounded-xl border border-blue-100 shadow-sm">
                      <h4 className="font-bold text-lg mb-4 text-gray-800 flex items-center gap-2">
                        <span className="w-8 h-8 bg-blue-600 text-white rounded-lg flex items-center justify-center text-sm">
                          Web
                        </span>
                        ウェブCM
                      </h4>
                      <div className="p-3 bg-white rounded-lg border border-blue-200">
                        <p className="text-xl font-bold text-blue-600">
                          {isMasked ? "🔒" : detailData.cost.webCm.range}
                        </p>
                      </div>
                    </div>
                  )}

                  {detailData.cost.event && (
                    <div className="p-5 bg-gradient-to-br from-purple-50 to-white rounded-xl border border-purple-100 shadow-sm">
                      <h4 className="font-bold text-lg mb-4 text-gray-800 flex items-center gap-2">
                        <span className="w-8 h-8 bg-purple-600 text-white rounded-lg flex items-center justify-center text-sm">
                          🎤
                        </span>
                        イベント出演
                      </h4>
                      <div className="p-3 bg-white rounded-lg border border-purple-200">
                        <p className="text-xl font-bold text-purple-600">
                          {isMasked ? "🔒" : detailData.cost.event.range}
                        </p>
                      </div>
                    </div>
                  )}

                  {detailData.cost.sns && (
                    <div className="p-5 bg-gradient-to-br from-pink-50 to-white rounded-xl border border-pink-100 shadow-sm">
                      <h4 className="font-bold text-lg mb-4 text-gray-800 flex items-center gap-2">
                        <span className="w-8 h-8 bg-pink-600 text-white rounded-lg flex items-center justify-center text-sm">
                          📱
                        </span>
                        SNS投稿
                      </h4>
                      <div className="p-3 bg-white rounded-lg border border-pink-200">
                        <p className="text-xl font-bold text-pink-600">{isMasked ? "🔒" : detailData.cost.sns.range}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {detailData.cost.packages && (
                <div className="mb-8">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-2xl">💼</span>
                    <h4 className="text-lg font-bold text-gray-700">パッケージ提案</h4>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(detailData.cost.packages).map(([key, pkg]) => (
                      <div
                        key={key}
                        className="p-5 bg-gradient-to-br from-blue-50 to-white rounded-xl border-2 border-blue-200 shadow-md hover:shadow-lg transition-shadow"
                      >
                        <h5 className="font-bold text-lg mb-3 text-gray-800">{pkg.name}</h5>
                        <div className="space-y-2 mb-4">
                          {pkg.contents.map((item, idx) => (
                            <div key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                              <span className="text-blue-600 mt-0.5">✨</span>
                              <span>{item}</span>
                            </div>
                          ))}
                        </div>
                        <div className="border-t border-blue-200 pt-4 space-y-2">
                          <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-600">通常価格</span>
                            <span className="line-through text-gray-400">{isMasked ? "🔒" : pkg.regularPrice}</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="font-semibold text-gray-700">パッケージ価格</span>
                            <span className="text-2xl font-bold text-blue-600">
                              {isMasked ? "🔒" : pkg.packagePrice}
                            </span>
                          </div>
                          <div className="bg-green-100 border border-green-300 rounded-lg p-3 mt-3">
                            <div className="flex items-center gap-2">
                              <span className="text-2xl">💰</span>
                              <span className="text-green-700 font-bold">{isMasked ? "🔒" : pkg.discount}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {detailData.cost.assetReuse && (
                <div className="mb-8">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-2xl">🔄</span>
                    <h4 className="text-lg font-bold text-gray-700">既存素材活用モデル</h4>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(detailData.cost.assetReuse).map(([key, model]) => (
                      <div
                        key={key}
                        className="p-5 bg-gradient-to-br from-amber-50 to-white rounded-xl border-2 border-amber-200 shadow-md hover:shadow-lg transition-shadow"
                      >
                        <h5 className="font-bold text-lg mb-2 text-gray-800">{model.name}</h5>
                        <p className="text-sm text-gray-600 mb-4">{model.description}</p>
                        <div className="space-y-3">
                          <div className="p-3 bg-white rounded-lg border border-gray-200">
                            <p className="text-xs text-gray-500 mb-1">通常制作費</p>
                            <p className="text-sm font-semibold text-gray-700 line-through">
                              {isMasked ? "🔒" : model.regularCost}
                            </p>
                          </div>
                          <div className="p-3 bg-amber-100 rounded-lg border border-amber-300">
                            <p className="text-xs text-gray-600 mb-1">活用時コスト</p>
                            <p className="text-lg font-bold text-amber-700">{isMasked ? "🔒" : model.reuseCost}</p>
                          </div>
                          <div className="bg-green-100 border border-green-300 rounded-lg p-3">
                            <div className="flex items-center gap-2">
                              <span className="text-2xl">💰</span>
                              <span className="text-green-700 font-bold">{isMasked ? "🔒" : model.savings}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {detailData.cost.designSets && (
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-2xl">🎨</span>
                    <h4 className="text-lg font-bold text-gray-700">デザイン・制作セット提案</h4>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(detailData.cost.designSets).map(([key, set]) => (
                      <div
                        key={key}
                        className="p-5 bg-gradient-to-br from-purple-50 to-white rounded-xl border-2 border-purple-200 shadow-md hover:shadow-lg transition-shadow"
                      >
                        <h5 className="font-bold text-lg mb-3 text-gray-800">{set.name}</h5>
                        <div className="space-y-2 mb-4">
                          {set.contents.map((item, idx) => (
                            <div key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                              <span className="text-purple-600 mt-0.5">✨</span>
                              <span>{item}</span>
                            </div>
                          ))}
                        </div>
                        <div className="border-t border-purple-200 pt-4 space-y-2">
                          <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-600">通常価格</span>
                            <span className="line-through text-gray-400">{isMasked ? "🔒" : set.regularPrice}</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="font-semibold text-gray-700">セット価格</span>
                            <span className="text-2xl font-bold text-purple-600">{isMasked ? "🔒" : set.setPrice}</span>
                          </div>
                          <div className="bg-green-100 border border-green-300 rounded-lg p-3 mt-3">
                            <div className="flex items-center gap-2">
                              <span className="text-2xl">💰</span>
                              <span className="text-green-700 font-bold">{isMasked ? "🔒" : set.discount}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </section>
          )}

          {/* CTA */}
          <div className="pt-6">
            <Button className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white py-6 text-lg font-bold shadow-lg hover:shadow-xl transition-all duration-300 rounded-xl">
              このタレントについて相談する
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
