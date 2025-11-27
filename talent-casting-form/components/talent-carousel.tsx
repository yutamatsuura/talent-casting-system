"use client"

import { useState, useMemo } from "react"
import { AlertCircle, User, ChevronLeft, ChevronRight, Star } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { TalentDetailModal } from "@/components/talent-detail-modal"
import type { Talent } from "@/lib/talent-data"
import { industryCodeMap } from "@/lib/talent-data"

type TalentCarouselProps = {
  talents: Talent[]
  selectedIndustry: string
  title?: string
  subtitle?: string
}

const industryKeyMap: Record<string, keyof Talent["industryFit"]> = {
  "美容・化粧品": "beauty_cosmetics",
  "食品・飲料": "food_beverage",
  "自動車・モビリティ": "automotive",
  "金融・保険": "finance_insurance",
  "IT・テクノロジー": "it_technology",
  "不動産・住宅": "real_estate",
  "小売・EC": "retail_ec",
  "ファッション・アパレル": "fashion_apparel",
  "ゲーム・エンタメ": "game_entertainment",
  "スポーツ・フィットネス": "sports_fitness",
  "旅行・ホテル": "travel_hotel",
  "教育・学習": "education",
  "医療・ヘルスケア": "medical_healthcare",
  "通信・キャリア": "telecom",
  "BtoB・法人向けサービス": "btob_services",
  "その他": "other",
}

export function TalentCarousel({ talents, selectedIndustry, title, subtitle }: TalentCarouselProps) {
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedTalent, setSelectedTalent] = useState<Talent | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const selectedIndustryCode = industryCodeMap[selectedIndustry] || ""

  const itemsPerPage = 9

  const sortedTalents = useMemo(() => {
    const talentsCopy = [...talents]

    const shuffled = [...talentsCopy]
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
    }

    const recommended = shuffled.slice(0, 3).map((t) => ({ ...t, isRecommended: true }))

    const remaining = talentsCopy
      .filter((t) => !recommended.find((r) => r.id === t.id))
      .sort((a, b) => b.matchScore - a.matchScore)
      .map((t) => ({ ...t, isRecommended: false }))

    const combined = [...recommended, ...remaining]

    return combined.slice(0, 20)
  }, [talents])

  const totalPages = Math.ceil(sortedTalents.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentTalents = sortedTalents.slice(startIndex, endIndex)

  const isInUseInIndustry = (talent: Talent) => {
    return talent.currentUsageIndustries.includes(selectedIndustryCode)
  }

  const goToPage = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  const goToPreviousPage = () => {
    if (currentPage > 1) {
      goToPage(currentPage - 1)
    }
  }

  const goToNextPage = () => {
    if (currentPage < totalPages) {
      goToPage(currentPage + 1)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h3 className="text-2xl font-bold text-foreground">{title || "おすすめタレント"}</h3>
        {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {currentTalents.map((talent) => {
          const inUse = isInUseInIndustry(talent)
          const isRecommended = talent.isRecommended

          return (
            <div
              key={talent.id}
              className={`bg-background rounded-xl shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden relative flex flex-col ${
                inUse ? "opacity-60" : ""
              }`}
            >
              {isRecommended && (
                <div className="absolute top-2 left-2 z-10 bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-2 py-0.5 rounded-full text-xs font-bold flex items-center gap-1 shadow-lg">
                  <Star className="h-3 w-3 fill-white" />
                  オススメ
                </div>
              )}

              {inUse && (
                <div className="absolute top-2 right-2 z-10 bg-red-500 text-white px-2 py-0.5 rounded-full text-xs font-bold flex items-center gap-1 shadow-lg">
                  <AlertCircle className="h-3 w-3" />
                  競合使用中
                </div>
              )}

              <div className="h-[80px] sm:h-[100px] lg:h-[120px] bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center relative">
                <div className="h-16 w-16 sm:h-20 sm:w-20 bg-white rounded-full flex items-center justify-center shadow-inner">
                  <User className="h-10 w-10 sm:h-12 sm:w-12 text-gray-400" strokeWidth={1.5} />
                </div>
              </div>

              <div className="p-3 flex flex-col flex-1">
                <div className="flex-1 flex items-center justify-center">
                  <h4 className="text-sm font-bold text-foreground text-center">{talent.name}</h4>
                </div>

                <div className="pt-2">
                  <Button
                    size="sm"
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white text-xs py-1.5"
                    onClick={() => {
                      setSelectedTalent(talent)
                      setIsModalOpen(true)
                    }}
                  >
                    詳細を見る
                  </Button>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-4">
          <Button
            variant="outline"
            size="icon"
            onClick={goToPreviousPage}
            disabled={currentPage === 1}
            className="h-10 w-10 bg-transparent"
          >
            <ChevronLeft className="h-5 w-5" />
          </Button>

          <div className="flex gap-2">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <Button
                key={page}
                variant={currentPage === page ? "default" : "outline"}
                size="icon"
                onClick={() => goToPage(page)}
                className="h-10 w-10"
              >
                {page}
              </Button>
            ))}
          </div>

          <Button
            variant="outline"
            size="icon"
            onClick={goToNextPage}
            disabled={currentPage === totalPages}
            className="h-10 w-10 bg-transparent"
          >
            <ChevronRight className="h-5 w-5" />
          </Button>
        </div>
      )}

      {selectedTalent && (
        <TalentDetailModal
          talent={selectedTalent}
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false)
            setSelectedTalent(null)
          }}
        />
      )}
    </div>
  )
}
