type Segment = {
  name: string
  description: string
  color: string
}

type SegmentLayer = "immediate" | "nurturing" | "exclusion"

export function getSegment(score: number): Segment {
  if (score >= 80) {
    return {
      name: "即アクション層",
      description: "今すぐキャスティングを検討したい企業様",
      color: "from-green-500 to-emerald-600",
    }
  } else if (score >= 50) {
    return {
      name: "育成層",
      description: "将来的にキャスティングを検討している企業様",
      color: "from-blue-500 to-cyan-600",
    }
  } else {
    return {
      name: "対象外層",
      description: "現在はキャスティングの対象外",
      color: "from-gray-500 to-slate-600",
    }
  }
}

export function getSegmentLayer(score: number): SegmentLayer {
  // Simplified segmentation based on score only since budget is removed
  if (score >= 70) {
    return "immediate"
  } else if (score >= 50) {
    return "nurturing"
  } else {
    return "exclusion"
  }
}
