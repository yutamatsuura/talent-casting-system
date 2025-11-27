"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Checkbox } from "@/components/ui/checkbox"
import { ChevronLeft, ChevronRight, Calendar, Home } from "lucide-react"
import { TalentCarousel } from "@/components/talent-carousel"
import { premiumTalents, middleTalents } from "@/lib/talent-data"
import { AnalysisLoadingScreen } from "@/components/analysis-loading-screen"
import { jsPDF } from "jspdf"
import { getSegment, getSegmentLayer } from "@/lib/segment-utils" // Import getSegment and getSegmentLayer

interface FormData {
  q2: string // Industry
  q3: string[] // Target demographics
  q3_2: string // Talent hiring reason
  q3_2_other: string // Other reason details
  q3_3: string // Budget
  q4: string // Company
  q5: string // Name
  q6: string // Email
  q7: string // Phone
  q7_2: string // Talent genre preference (希望ジャンルなし or 希望ジャンルあり)
  q7_2_genres: string[] // Selected genres when 希望ジャンルあり
  privacyAgreed: boolean
}

const STORAGE_KEY = "talent-casting-form-data"

const formatPurposes = (formData: FormData): string => {
  if (!Array.isArray(formData.q10) || formData.q10.length === 0) {
    return "ブランディングや認知度向上"
  }
  return formData.q10.join("、")
}

const generatePersonalizedMessage = (formData: FormData): string => {
  const companyName = formData.q4 || "貴社"
  const industry = formData.q2 || "業界"
  const purposes = Array.isArray(formData.q10) && formData.q10.length > 0 ? formData.q10.join("や") : "ブランド価値向上"

  return `${companyName}様の${industry}における${purposes}の実現に向けて、最適なタレントをご提案いたします。`
}

export default function TalentCastingForm() {
  const [currentStep, setCurrentStep] = useState(1)
  const [score, setScore] = useState(0)
  const [formData, setFormData] = useState<FormData>({
    q2: "",
    q3: [],
    q3_2: "",
    q3_2_other: "",
    q3_3: "",
    q4: "",
    q5: "",
    q6: "",
    q7: "",
    q7_2: "希望ジャンルなし",
    q7_2_genres: [],
    privacyAgreed: false,
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [showResults, setShowResults] = useState(false)
  const [showLoading, setShowLoading] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        const merged = {
          ...formData,
          ...parsed,
          q3: Array.isArray(parsed.q3) ? parsed.q3 : [],
          q7_2_genres: Array.isArray(parsed.q7_2_genres) ? parsed.q7_2_genres : [],
          privacyAgreed: false,
        }
        setFormData(merged)
        setScore(parsed.score || 0)
        setCurrentStep(parsed.currentStep || 1)
      } catch (e) {
        console.error("Failed to parse saved data")
      }
    }
  }, [])

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ formData, score, currentStep }))
  }, [formData, score, currentStep])

  const totalSteps = 6

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {}

    if (step === 1) {
      if (!formData.q2) newErrors.q2 = "業界を選択してください"
    }

    if (step === 2) {
      if (!Array.isArray(formData.q3) || formData.q3.length === 0) {
        newErrors.q3 = "少なくとも1つのターゲット層を選択してください"
      }
    }

    if (step === 3) {
      if (!formData.q3_2) newErrors.q3_2 = "理由を選択してください"
      if (formData.q3_2 === "その他" && !formData.q3_2_other) {
        newErrors.q3_2_other = "詳細を入力してください"
      }
    }

    if (step === 4) {
      if (!formData.q3_3) newErrors.q3_3 = "予算を選択してください"
    }

    if (step === 5) {
      if (!formData.q4) newErrors.q4 = "会社名を入力してください"
      if (!formData.q5) newErrors.q5 = "お名前を入力してください"
      if (!formData.q6) newErrors.q6 = "メールアドレスを入力してください"
      if (!formData.q7) newErrors.q7 = "電話番号を入力してください"
      if (formData.q6 && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.q6)) {
        newErrors.q6 = "有効なメールアドレスを入力してください"
      }
    }

    if (step === 6) {
      if (!formData.privacyAgreed) {
        newErrors.privacyAgreed = "プライバシーポリシーへの同意が必要です"
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleNext = () => {
    if (validateStep(currentStep)) {
      if (currentStep < totalSteps) {
        setCurrentStep(currentStep + 1)
      } else {
        setScore(calculateScore())
        setIsAnalyzing(true)
        setShowLoading(true)
        setTimeout(() => {
          setShowLoading(false)
          setShowResults(true)
        }, 5000)
      }
    }
  }

  const handleBack = () => {
    setCurrentStep(Math.max(1, currentStep - 1))
  }

  const handleReset = () => {
    setFormData({
      q2: "",
      q3: [],
      q3_2: "",
      q3_2_other: "",
      q3_3: "",
      q4: "",
      q5: "",
      q6: "",
      q7: "",
      q7_2: "希望ジャンルなし",
      q7_2_genres: [],
      privacyAgreed: false,
    })
    setScore(0)
    setCurrentStep(1)
    setShowResults(false)
    setShowLoading(false)
    setErrors({})
    localStorage.removeItem(STORAGE_KEY)
  }

  const calculateScore = (): number => {
    let points = 0

    if (formData.q2) points += 10
    if (formData.q3.length > 0) points += 10
    if (formData.q3_2) points += 15
    if (formData.q3_3) points += 15

    points += 50

    return Math.min(points, 100)
  }

  const progress = (currentStep / totalSteps) * 100

  const renderMessageWithLargeCompanyName = (message: string) => {
    const companyName = formData.q4 || "貴社"
    const companyPattern = `${companyName}様`

    if (message.includes(companyPattern)) {
      const parts = message.split(companyPattern)
      return (
        <>
          <span className="text-xl font-bold text-blue-700">{companyPattern}</span>
          {parts[1]}
        </>
      )
    }
    return message
  }

  const generatePDF = () => {
    const doc = new jsPDF()
    const companyName = formData.q4 || "貴社"

    // Header
    doc.setFontSize(16)
    doc.text(`${companyName}様`, 105, 20, { align: "center" })

    // Title
    doc.setFontSize(14)
    doc.text("株式会社e-Spirit キャスティングリスト", 105, 35, { align: "center" })

    // Line separator
    doc.setLineWidth(0.5)
    doc.line(20, 45, 190, 45)

    // Talent list
    doc.setFontSize(12)
    let yPosition = 60
    const talents = getSegmentLayer(score, formData.q2) === "immediate" ? premiumTalents : middleTalents
    const sortedTalents = [...talents].sort((a, b) => a.kana.localeCompare(b.kana, "ja")).slice(0, 20)

    sortedTalents.forEach((talent, index) => {
      if (yPosition > 250) {
        doc.addPage()
        yPosition = 20
      }

      // Talent name with number
      doc.text(`${index + 1}. ${talent.name}`, 30, yPosition)
      yPosition += 10
    })

    // Footer
    if (yPosition > 240) {
      doc.addPage()
      yPosition = 20
    }

    doc.setLineWidth(0.5)
    doc.line(20, yPosition + 10, 190, yPosition + 10)

    doc.setFontSize(12)
    doc.text("詳しい情報を知りたい方はこちらから", 105, yPosition + 25, { align: "center" })

    doc.setFontSize(10)
    doc.setTextColor(0, 0, 255)
    doc.textWithLink("打ち合わせ面談日時を設定する", 105, yPosition + 35, {
      align: "center",
      url: "https://app.spirinc.com/t/W63rJQN01CTXR-FjsFaOr/as/8FtIxQriLEvZxYqBlbzib/confirm",
    })

    // Save PDF
    doc.save(`${companyName}_キャスティングリスト.pdf`)
  }

  if (showLoading) {
    return (
      <AnalysisLoadingScreen
        onComplete={() => {
          setShowLoading(false)
          setShowResults(true)
        }}
      />
    )
  }

  if (showResults) {
    const segment = getSegment(score)
    const segmentLayer = getSegmentLayer(score, formData.q2)
    const personalizedMessage = generatePersonalizedMessage(formData)

    if (segmentLayer === "exclusion") {
      return (
        <div className="min-h-screen flex items-center justify-center p-4">
          <Card className="w-full max-w-2xl shadow-lg">
            <CardHeader className="text-center space-y-4 pb-8">
              <CardTitle className="text-3xl font-bold text-balance">診断結果</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 border-l-4 border-blue-500 p-6 rounded-r-lg shadow-sm space-y-4">
                <p className="text-base leading-relaxed text-gray-800">
                  {renderMessageWithLargeCompanyName(personalizedMessage)}
                </p>
              </div>

              <div className="text-center space-y-4">
                <Button
                  size="lg"
                  variant="outline"
                  className="w-full sm:w-auto text-lg px-8 py-6 bg-transparent"
                  onClick={() => (window.location.href = "/")}
                >
                  <Home className="mr-2 h-5 w-5" />
                  ホームページに戻る
                </Button>

                <Button variant="ghost" onClick={handleReset} className="w-full sm:w-auto">
                  最初からやり直す
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    if (segmentLayer === "immediate") {
      return (
        <div className="min-h-screen flex items-center justify-center p-4">
          <Card className="w-full max-w-5xl shadow-lg">
            <CardHeader className="text-center space-y-4 pb-8">
              <CardTitle className="text-3xl font-bold text-balance">診断結果</CardTitle>
            </CardHeader>
            <CardContent className="space-y-8">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 border-l-4 border-blue-500 p-6 rounded-r-lg shadow-sm space-y-4">
                <p className="text-base leading-relaxed text-gray-800">
                  {renderMessageWithLargeCompanyName(personalizedMessage)}
                </p>
              </div>

              <TalentCarousel
                talents={premiumTalents}
                selectedIndustry={formData.q2}
                title="おすすめタレント"
                subtitle="合計60,000名中、上位30名から厳選してご提案"
              />

              <div className="text-center space-y-4">
                <Button
                  size="lg"
                  className="w-full px-6 py-6 text-lg shadow-lg bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
                  onClick={() =>
                    window.open(
                      "https://app.spirinc.com/t/W63rJQN01CTXR-FjsFaOr/as/8FtIxQriLEvZxYqBlbzib/confirm",
                      "_blank",
                    )
                  }
                >
                  <Calendar className="mr-2 h-5 w-5" />
                  今すぐ無料カウンセリングを予約する
                </Button>

                <Button variant="ghost" onClick={handleReset} className="w-full sm:w-auto text-sm">
                  最初からやり直す
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-5xl shadow-lg">
          <CardHeader className="text-center space-y-4 pb-8">
            <CardTitle className="text-3xl font-bold text-balance">診断結果</CardTitle>
          </CardHeader>
          <CardContent className="space-y-8">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 border-l-4 border-blue-500 p-6 rounded-r-lg shadow-sm space-y-4">
              <p className="text-base leading-relaxed text-gray-800">
                {renderMessageWithLargeCompanyName(generatePersonalizedMessage(formData))}
              </p>
            </div>

            <TalentCarousel
              talents={getSegmentLayer(score, formData.q2) === "immediate" ? premiumTalents : middleTalents}
              selectedIndustry={formData.q2}
              title="おすすめタレント"
              subtitle="合計60,000名中、上位30名から厳選してご提案"
            />

            <div className="text-center space-y-4">
              <Button
                size="lg"
                className="w-full px-6 py-6 text-lg shadow-lg bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
                onClick={() =>
                  window.open(
                    "https://app.spirinc.com/t/W63rJQN01CTXR-FjsFaOr/as/8FtIxQriLEvZxYqBlbzib/confirm",
                    "_blank",
                  )
                }
              >
                <Calendar className="mr-2 h-5 w-5" />
                今すぐ無料カウンセリングを予約する
              </Button>

              <Button variant="ghost" onClick={handleReset} className="w-full sm:w-auto text-sm">
                最初からやり直す
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
      {!showResults && !showLoading && (
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <div className="space-y-2">
              <div className="w-full bg-muted rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${(currentStep / totalSteps) * 100}%` }}
                />
              </div>
              <p className="text-sm text-muted-foreground text-center">
                質問 {currentStep} / {totalSteps}
              </p>
              <CardTitle className="text-2xl text-center">タレントキャスティング診断</CardTitle>
            </div>
          </CardHeader>

          <CardContent>
            {currentStep === 1 && (
              <div className="space-y-6">
                <div className="space-y-4">
                  <Label className="text-lg font-semibold">貴社の業界は次のうちどれにあてはまりますか？</Label>
                  <p className="text-sm text-muted-foreground mt-1">
                    ※業界に最適なタレントをご提案するために使用します
                  </p>
                  <RadioGroup value={formData.q2} onValueChange={(value) => setFormData({ ...formData, q2: value })}>
                    <div className="space-y-3 max-h-96 overflow-y-auto border rounded-lg p-4 bg-white">
                      {[
                        "食品",
                        "菓子・氷菓",
                        "乳製品",
                        "清涼飲料水",
                        "アルコール飲料",
                        "フードサービス",
                        "医薬品・医療・健康食品",
                        "化粧品・ヘアケア・オーラルケア",
                        "トイレタリー",
                        "自動車関連",
                        "家電",
                        "通信・IT",
                        "ゲーム・エンターテイメント・アプリ",
                        "流通・通販",
                        "ファッション",
                        "貴金属",
                        "金融・不動産",
                        "エネルギー・輸送・交通",
                        "教育・出版・公共団体",
                        "観光",
                      ].map((industry) => (
                        <div key={industry} className="flex items-center space-x-2">
                          <RadioGroupItem value={industry} id={industry} />
                          <Label htmlFor={industry} className="cursor-pointer">
                            {industry}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </RadioGroup>
                  {errors.q2 && <p className="text-sm text-destructive">{errors.q2}</p>}
                </div>
              </div>
            )}

            {currentStep === 2 && (
              <div className="space-y-4">
                <div>
                  <Label className="text-lg font-semibold">貴社の商品サービスの主要なターゲットはどの層ですか？</Label>
                  <p className="text-sm text-muted-foreground mt-1">※例）商品を買っていただけるであろう層</p>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    "男性12-19",
                    "女性12-19",
                    "男性20-34",
                    "女性20-34",
                    "男性35-49",
                    "女性35-49",
                    "男性50-69",
                    "女性50-69",
                  ].map((option) => (
                    <div key={option} className="flex items-center space-x-2 p-3 rounded-lg hover:bg-muted">
                      <Checkbox
                        id={option}
                        checked={Array.isArray(formData.q3) && formData.q3.includes(option)}
                        onCheckedChange={(checked) => {
                          const currentQ3 = Array.isArray(formData.q3) ? formData.q3 : []
                          setFormData({
                            ...formData,
                            q3: checked ? [...currentQ3, option] : currentQ3.filter((item) => item !== option),
                          })
                        }}
                      />
                      <Label htmlFor={option} className="cursor-pointer text-sm">
                        {option}
                      </Label>
                    </div>
                  ))}
                </div>
                {errors.q3 && <p className="text-sm text-destructive">{errors.q3}</p>}
              </div>
            )}

            {currentStep === 3 && (
              <div className="space-y-4">
                <Label className="text-lg font-semibold">タレント起用を検討する一番の理由はなんですか？</Label>
                <RadioGroup
                  value={formData.q3_2}
                  onValueChange={(value) => setFormData({ ...formData, q3_2: value, q3_2_other: "" })}
                >
                  {[
                    "商品サービスの知名度アップ",
                    "商品サービスの売上拡大",
                    "商品サービスの特長訴求のため",
                    "企業知名度アップ",
                    "企業好感度アップ",
                    "採用効果アップ",
                    "その他",
                  ].map((option) => (
                    <div
                      key={option}
                      className="flex items-center space-x-3 p-3 rounded-lg hover:bg-muted transition-colors"
                    >
                      <RadioGroupItem value={option} id={`reason-${option}`} />
                      <Label htmlFor={`reason-${option}`} className="cursor-pointer flex-1 text-base">
                        {option}
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
                {formData.q3_2 === "その他" && (
                  <div className="mt-4">
                    <Input
                      placeholder="詳細を入力してください"
                      value={formData.q3_2_other}
                      onChange={(e) => setFormData({ ...formData, q3_2_other: e.target.value })}
                    />
                    {errors.q3_2_other && <p className="text-sm text-destructive mt-1">{errors.q3_2_other}</p>}
                  </div>
                )}
                {errors.q3_2 && <p className="text-sm text-destructive">{errors.q3_2}</p>}
              </div>
            )}

            {currentStep === 4 && (
              <div className="space-y-4">
                <Label className="text-lg font-semibold">今回の施策のタレント予算はどの程度ですか？</Label>
                <RadioGroup value={formData.q3_3} onValueChange={(value) => setFormData({ ...formData, q3_3: value })}>
                  {["1,000万円未満", "1,000万円～3,000万円未満", "3,000万円～1億円未満", "1億円以上"].map((option) => (
                    <div
                      key={option}
                      className="flex items-center space-x-3 p-3 rounded-lg hover:bg-muted transition-colors"
                    >
                      <RadioGroupItem value={option} id={`budget-${option}`} />
                      <Label htmlFor={`budget-${option}`} className="cursor-pointer flex-1 text-base">
                        {option}
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
                {errors.q3_3 && <p className="text-sm text-destructive">{errors.q3_3}</p>}
              </div>
            )}

            {currentStep === 5 && (
              <div className="space-y-6">
                <Label className="text-lg font-semibold">貴社の情報を教えてください</Label>

                <div className="space-y-2">
                  <Label htmlFor="company">貴社名</Label>
                  <Input
                    id="company"
                    placeholder="例：株式会社〇〇"
                    value={formData.q4}
                    onChange={(e) => setFormData({ ...formData, q4: e.target.value })}
                  />
                  {errors.q4 && <p className="text-sm text-destructive">{errors.q4}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="name">ご担当者名</Label>
                  <Input
                    id="name"
                    placeholder="例：山田 太郎"
                    value={formData.q5}
                    onChange={(e) => setFormData({ ...formData, q5: e.target.value })}
                  />
                  {errors.q5 && <p className="text-sm text-destructive">{errors.q5}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">メールアドレス</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="例：example@company.com"
                    value={formData.q6}
                    onChange={(e) => setFormData({ ...formData, q6: e.target.value })}
                  />
                  <p className="text-sm text-muted-foreground">
                    ※タレントリストをお送りしますので、正確にご記入ください。
                  </p>
                  {errors.q6 && <p className="text-sm text-destructive">{errors.q6}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">携帯電話番号</Label>
                  <Input
                    id="phone"
                    type="tel"
                    placeholder="例：090-1234-5678"
                    value={formData.q7}
                    onChange={(e) => setFormData({ ...formData, q7: e.target.value })}
                  />
                  {errors.q7 && <p className="text-sm text-destructive">{errors.q7}</p>}
                </div>

                <div className="space-y-3">
                  <Label>起用したいタレントのジャンル(俳優・アーティスト等)はありますか？</Label>
                  <p className="text-sm text-muted-foreground">※AIの診断結果には影響しません</p>

                  <RadioGroup
                    value={formData.q7_2}
                    onValueChange={(value) => {
                      setFormData({
                        ...formData,
                        q7_2: value,
                        q7_2_genres: value === "希望ジャンルなし" ? [] : formData.q7_2_genres,
                      })
                    }}
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="希望ジャンルなし" id="no-genre" />
                      <Label htmlFor="no-genre" className="font-normal cursor-pointer">
                        希望ジャンルなし
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="希望ジャンルあり" id="has-genre" />
                      <Label htmlFor="has-genre" className="font-normal cursor-pointer">
                        希望ジャンルあり
                      </Label>
                    </div>
                  </RadioGroup>

                  {formData.q7_2 === "希望ジャンルあり" && (
                    <div className="ml-6 space-y-2 mt-3">
                      {[
                        "俳優",
                        "モデル",
                        "アーティスト",
                        "声優・ナレーター",
                        "アイドル",
                        "お笑い芸人",
                        "アスリート",
                      ].map((genre) => (
                        <div key={genre} className="flex items-center space-x-2">
                          <Checkbox
                            id={`genre-${genre}`}
                            checked={Array.isArray(formData.q7_2_genres) && formData.q7_2_genres.includes(genre)}
                            onCheckedChange={(checked) => {
                              const currentGenres = Array.isArray(formData.q7_2_genres) ? formData.q7_2_genres : []
                              if (checked) {
                                setFormData({ ...formData, q7_2_genres: [...currentGenres, genre] })
                              } else {
                                setFormData({ ...formData, q7_2_genres: currentGenres.filter((g) => g !== genre) })
                              }
                            }}
                          />
                          <Label htmlFor={`genre-${genre}`} className="font-normal cursor-pointer">
                            {genre}
                          </Label>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {currentStep === 6 && (
              <div className="space-y-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">利用規約についてのご同意</h3>
                  <div className="bg-muted p-4 rounded-lg space-y-2 text-sm">
                    <p className="font-medium">当サービスの利用規約をご覧ください。</p>
                    <p>
                      ご入力いただいた情報は、診断結果の提供、タレントキャスティングに関する情報提供、お問い合わせ対応のために使用いたします。
                    </p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <Checkbox
                      id="privacy"
                      checked={formData.privacyAgreed}
                      onCheckedChange={(checked) => setFormData({ ...formData, privacyAgreed: checked === true })}
                    />
                    <Label htmlFor="privacy" className="cursor-pointer font-normal leading-relaxed">
                      当サービスの利用規約に同意する
                    </Label>
                  </div>
                  {errors.privacyAgreed && <p className="text-sm text-destructive">{errors.privacyAgreed}</p>}
                </div>
              </div>
            )}
          </CardContent>

          <CardFooter className="flex justify-between">
            <Button variant="outline" onClick={handleBack} disabled={currentStep === 1}>
              <ChevronLeft className="mr-2 h-4 w-4" />
              戻る
            </Button>
            <Button onClick={handleNext}>
              {currentStep === 6 ? "結果を見る" : "次へ"}
              {currentStep !== 6 && <ChevronRight className="ml-2 h-4 w-4" />}
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  )
}
