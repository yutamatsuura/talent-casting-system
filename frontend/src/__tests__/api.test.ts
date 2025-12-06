/**
 * API utility functions tests
 * Tests for callMatchingApi, checkApiHealth, and fetchTalentDetails functions
 */

import { callMatchingApi, checkApiHealth, fetchTalentDetails } from '@/lib/api'
import { FormData } from '@/types'

// Mock fetch globally
global.fetch = jest.fn()
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>

describe('API Utility Functions', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  describe('checkApiHealth', () => {
    it('should return true when API is healthy', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'healthy', database: 'connected' }),
      } as Response)

      const result = await checkApiHealth()
      expect(result).toBe(true)
    })

    it('should return false when API is unhealthy', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'unhealthy', database: 'disconnected' }),
      } as Response)

      const result = await checkApiHealth()
      expect(result).toBe(false)
    })

    it('should return false when fetch fails', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      const result = await checkApiHealth()
      expect(result).toBe(false)
    })
  })

  describe('callMatchingApi', () => {
    const mockFormData: FormData = {
      q2: '化粧品・ヘアケア・オーラルケア',
      q3: '女性20-34歳',
      q3_2: '商品認知向上',
      q3_3: '1,000万円～3,000万円未満',
      q4: 'テスト株式会社',
      q5: 'テスト太郎',
      q6: 'test@example.com',
      q7: '090-1234-5678',
      q7_2: '希望ジャンルなし',
      q7_2_genres: [],
      privacyAgreed: true,
    }

    it('should return talent results on successful API call', async () => {
      const mockApiResponse = {
        success: true,
        total_results: 30,
        results: [
          {
            talent_id: 1,
            account_id: 101,
            name: 'テストタレント',
            kana: 'テストタレント',
            category: '俳優',
            matching_score: 95.5,
            ranking: 1,
            base_power_score: 88.0,
            image_adjustment: 7.5,
            is_recommended: true,
            is_currently_in_cm: false,
          },
        ],
        processing_time_ms: 245,
        timestamp: new Date().toISOString(),
        session_id: 'test-session-123',
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockApiResponse,
      } as Response)

      const result = await callMatchingApi(mockFormData)

      expect(result.results).toHaveLength(1)
      expect(result.results[0].name).toBe('テストタレント')
      expect(result.results[0].matching_score).toBe(95.5)
      expect(result.sessionId).toBe('test-session-123')
    })

    it('should throw error on API failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => 'Server error occurred',
      } as Response)

      await expect(callMatchingApi(mockFormData)).rejects.toThrow(
        'API Error: 500 Internal Server Error - Server error occurred'
      )
    })

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network connection failed'))

      await expect(callMatchingApi(mockFormData)).rejects.toThrow(
        'Network connection failed'
      )
    })
  })

  describe('fetchTalentDetails', () => {
    it('should return talent details successfully', async () => {
      const mockTalentDetail = {
        account_id: 101,
        name: 'テストタレント',
        kana: 'テストタレント',
        category: '俳優',
        age: 28,
        company_name: 'テストプロダクション',
        introduction: 'テストタレントの紹介文',
        matching_score: 95.5,
        ranking: 1,
        cm_history: [
          {
            company_name: 'テスト企業',
            industry_name: '化粧品',
            start_date: '2023-01-01',
            end_date: '2023-12-31',
          },
        ],
        base_power_score: 88.0,
        image_adjustment: 7.5,
        image_url: '/test-talent.jpg',
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTalentDetail,
      } as Response)

      const result = await fetchTalentDetails(101, 1)

      expect(result.name).toBe('テストタレント')
      expect(result.account_id).toBe(101)
      expect(result.cm_history).toHaveLength(1)
    })

    it('should throw error when talent not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        text: async () => 'Talent not found',
      } as Response)

      await expect(fetchTalentDetails(999)).rejects.toThrow(
        'タレント詳細情報の取得に失敗しました'
      )
    })
  })
})