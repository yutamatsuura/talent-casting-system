"use client"

import { useState, useEffect } from "react"
import { Search, BarChart3, CheckCircle, Loader2, Circle, Sparkles } from "lucide-react"

type AnalysisStep = {
  id: number
  title: string
  description: string
  duration: number
  processingText: string
  maxCount: number
}

const steps: AnalysisStep[] = [
  {
    id: 1,
    title: "業界データベース検索",
    description: "2,500件のタレントデータを分析",
    duration: 1500,
    processingText: "処理中",
    maxCount: 2500,
  },
  {
    id: 2,
    title: "ターゲット層マッチング",
    description: "F1・F2層データとのクロス分析",
    duration: 1000,
    processingText: "処理中",
    maxCount: 20,
  },
  {
    id: 3,
    title: "CM出演実績の照合",
    description: "過去5年間のCMデータを検証",
    duration: 2000,
    processingText: "処理中",
    maxCount: 3500,
  },
  {
    id: 4,
    title: "起用コスト最適化",
    description: "予算シミュレーション実行",
    duration: 1000,
    processingText: "最適プランを計算中...",
    maxCount: 100,
  },
  {
    id: 5,
    title: "競合起用状況チェック",
    description: "最新の契約状況を確認",
    duration: 1000,
    processingText: "バッティング確認中...",
    maxCount: 100,
  },
  {
    id: 6,
    title: "総合スコア算出",
    description: "マッチング精度を計算",
    duration: 1000,
    processingText: "スコアリング中...",
    maxCount: 100,
  },
]

export function AnalysisLoadingScreen({ onComplete }: { onComplete: () => void }) {
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState(0)

  useEffect(() => {
    const totalDuration = steps.reduce((sum, step) => sum + step.duration, 0)
    let elapsed = 0

    const interval = setInterval(() => {
      elapsed += 50
      const newProgress = Math.min((elapsed / totalDuration) * 100, 100)
      setProgress(newProgress)

      // Calculate current step based on elapsed time
      let cumulativeDuration = 0
      for (let i = 0; i < steps.length; i++) {
        cumulativeDuration += steps[i].duration
        if (elapsed < cumulativeDuration) {
          setCurrentStep(i)
          break
        }
      }

      if (elapsed >= totalDuration) {
        clearInterval(interval)
        setTimeout(() => {
          onComplete()
        }, 500)
      }
    }, 50)

    return () => clearInterval(interval)
  }, [onComplete])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-2xl w-full mx-auto">
        {/* ヘッダー */}
        <div className="text-center mb-8">
          <div className="inline-block p-3 bg-blue-600 rounded-full mb-3 animate-pulse">
            <Search className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">AIマッチング分析中</h1>
          <p className="text-sm text-gray-600">貴社に最適なタレントを解析しています</p>
        </div>

        {/* プログレスバー */}
        <div className="mb-8">
          <div className="w-full bg-gray-200 rounded-full h-3 mb-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-500 to-indigo-600 h-3 rounded-full transition-all duration-300 ease-out relative"
              style={{ width: `${progress}%` }}
            >
              <div className="absolute inset-0 bg-white opacity-20 animate-pulse"></div>
            </div>
          </div>
          <div className="text-right text-xl font-bold text-blue-600">{Math.round(progress)}%</div>
        </div>

        {/* 分析ステップ */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2 text-blue-600" />
            分析ステップ
          </h2>

          <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className={`flex items-start space-x-3 rounded-lg transition-all duration-500 ease-in-out ${
                  index < currentStep
                    ? "bg-green-50 border border-green-200 p-2" // 完了ステップは小さく
                    : index === currentStep
                      ? "bg-blue-50 border border-blue-200 p-4 animate-pulse" // 処理中ステップは通常サイズ
                      : "bg-gray-50 border border-gray-200 p-2 opacity-40" // 待機中ステップは小さく
                }`}
              >
                {/* アイコン */}
                <div className="flex-shrink-0 mt-0.5">
                  {index < currentStep ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : index === currentStep ? (
                    <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                  ) : (
                    <Circle className="w-5 h-5 text-gray-400" />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <h3
                    className={`font-semibold mb-0.5 ${
                      index < currentStep
                        ? "text-sm text-gray-700" // 完了ステップは小さいフォント
                        : index === currentStep
                          ? "text-base text-gray-900" // 処理中ステップは通常フォント
                          : "text-sm text-gray-500" // 待機中ステップは小さいフォント
                    }`}
                  >
                    {step.title}
                  </h3>

                  {index === currentStep && (
                    <>
                      <p className="text-sm text-gray-600 mb-2">{step.description}</p>
                      <div className="space-y-2">
                        <p className="text-xs text-blue-600 font-medium">{step.processingText}</p>
                        <div className="w-full bg-blue-100 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{
                              width: `${((progress % (100 / steps.length)) / (100 / steps.length)) * 100}%`,
                            }}
                          ></div>
                        </div>
                      </div>
                    </>
                  )}

                  {index < currentStep && <p className="text-xs text-green-600 font-medium">✓ 完了</p>}

                  {index > currentStep && <p className="text-xs text-gray-400">待機中</p>}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-4 text-white text-center">
          <div className="flex items-center justify-center mb-1">
            <Sparkles className="w-4 h-4 mr-2" />
            <span className="text-xs font-medium">高度なAIアルゴリズム</span>
          </div>
          <p className="text-xs opacity-90">20,000以上のデータポイントから最適なタレントを選定</p>
        </div>
      </div>
    </div>
  )
}
