"""SQLAlchemyモデル定義（単一真実源の原則）"""
from sqlalchemy import Column, Integer, String, ForeignKey, Index, DateTime, Numeric, Date, Boolean, Text, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class Industry(Base):
    """業種マスタテーブル（実際のDB構造に準拠）"""
    __tablename__ = "industries"

    industry_id = Column("industry_id", Integer, primary_key=True, autoincrement=True)
    industry_name = Column("industry_name", String(255), nullable=False)
    required_image_id = Column("required_image_id", Integer, nullable=True)
    created_at = Column("created_at", DateTime, nullable=True)
    updated_at = Column("updated_at", DateTime, nullable=True)

    # 互換性のためのプロパティ
    @property
    def id(self):
        return self.industry_id

    @property
    def name(self):
        return self.industry_name

    @property
    def display_order(self):
        return self.industry_id  # industry_idを順序として使用

    # リレーション
    industry_images = relationship("IndustryImage", back_populates="industry", foreign_keys="IndustryImage.industry_id")

    def __repr__(self):
        return f"<Industry(industry_id={self.industry_id}, industry_name='{self.industry_name}')>"


class ImageItem(Base):
    """イメージ項目マスタテーブル（requirements.md準拠）"""
    __tablename__ = "image_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    display_order = Column(Integer, default=0)

    # リレーション
    industry_images = relationship("IndustryImage", back_populates="image_item")

    def __repr__(self):
        return f"<ImageItem(id={self.id}, code='{self.code}', name='{self.name}')>"


class IndustryImage(Base):
    """業種-イメージ紐付けテーブル（STEP2業種イメージ査定用）"""
    __tablename__ = "industry_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    industry_id = Column(Integer, ForeignKey("industries.industry_id", ondelete="CASCADE"), nullable=False)
    image_item_id = Column(Integer, ForeignKey("image_items.id", ondelete="CASCADE"), nullable=False)

    # リレーション
    industry = relationship("Industry", back_populates="industry_images")
    image_item = relationship("ImageItem", back_populates="industry_images")

    # 複合ユニーク制約
    __table_args__ = (
        Index("idx_industry_images_lookup", "industry_id", "image_item_id", unique=True),
    )

    def __repr__(self):
        return f"<IndustryImage(industry_id={self.industry_id}, image_item_id={self.image_item_id})>"


class TargetSegment(Base):
    """ターゲット層マスタテーブル（新DB構造対応）
    8ターゲット層の管理（男性・女性 × 4年齢区分）
    VR/TPRデータとの紐付けに使用（target_segment_id: 9-16）
    """

    __tablename__ = "target_segments"

    target_segment_id = Column(Integer, primary_key=True, autoincrement=True)
    segment_name = Column(String(50), nullable=False)
    gender = Column(String(10), nullable=True)
    age_min = Column(Integer, nullable=True)
    age_max = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # インデックス定義
    __table_args__ = (
        Index("idx_target_segments_id", "target_segment_id"),
    )

    def __repr__(self) -> str:
        return f"<TargetSegment(target_segment_id={self.target_segment_id}, segment_name='{self.segment_name}')>"


class BudgetRange(Base):
    """予算区分マスタテーブル（requirements.md準拠）"""
    __tablename__ = "budget_ranges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    min_amount = Column(Numeric(12, 2), nullable=True)
    max_amount = Column(Numeric(12, 2), nullable=True)
    display_order = Column(Integer, default=0)

    def __repr__(self):
        return f"<BudgetRange(id={self.id}, name='{self.name}')>"


class Talent(Base):
    """タレント基本情報テーブル（m_account実体に対応）

    注意: このモデルは m_account テーブルに対応しています。
    実際のマッチングクエリでは直接SQLを使用するため、
    このモデルは主に管理・参照用として定義されています。
    """
    __tablename__ = "m_account"

    account_id = Column(Integer, primary_key=True, autoincrement=True)
    name_full_for_matching = Column(String(255), nullable=False, index=True)
    last_name_kana = Column(String(255), nullable=True)
    first_name_kana = Column(String(255), nullable=True)
    act_genre = Column(String(100), nullable=True)
    gender = Column(String(10), nullable=True)
    birthday = Column(Date, nullable=True)
    company_name = Column(String(255), nullable=True, index=True)
    image_name = Column(String(255), nullable=True)
    pref_cd = Column(Integer, nullable=True)
    url = Column(String(1000), nullable=True)
    del_flag = Column(Integer, default=0, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション（talent_scores/talent_imagesは account_id で参照）
    talent_scores = relationship("TalentScore", back_populates="talent", cascade="all, delete-orphan", foreign_keys="TalentScore.account_id")
    talent_images = relationship("TalentImage", back_populates="talent", cascade="all, delete-orphan", foreign_keys="TalentImage.account_id")
    talent_act = relationship("TalentAct", back_populates="account", uselist=False)
    cm_history = relationship("MTalentCm", back_populates="talent", cascade="all, delete-orphan", foreign_keys="MTalentCm.account_id")

    # インデックス
    __table_args__ = (
        Index("idx_m_account_act_genre", "act_genre"),
        Index("idx_m_account_name", "name_full_for_matching"),
        Index("idx_m_account_del_flag", "del_flag"),
        Index("idx_m_account_company", "company_name"),
        Index("idx_m_account_birthday", "birthday"),
    )

    def __repr__(self):
        return f"<Talent(account_id={self.account_id}, name='{self.name_full_for_matching}')>"


class TalentAct(Base):
    """タレント活動情報テーブル（m_talent_act実体に対応）

    注意: このテーブルは m_talent_act に対応し、
    主に予算情報（money_max_one_year）を管理します。
    """
    __tablename__ = "m_talent_act"

    account_id = Column(Integer, ForeignKey("m_account.account_id", ondelete="CASCADE"), primary_key=True)
    money_max_one_year = Column(Numeric(12, 2), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション
    account = relationship("Talent", back_populates="talent_act")

    # インデックス
    __table_args__ = (
        Index("idx_m_talent_act_money", "money_max_one_year"),
    )

    def __repr__(self):
        return f"<TalentAct(account_id={self.account_id}, money_max_one_year={self.money_max_one_year})>"


class TalentScore(Base):
    """タレントスコアテーブル（VR/TPRデータ統合、requirements.md準拠）"""
    __tablename__ = "talent_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("m_account.account_id", ondelete="CASCADE"), nullable=False)
    target_segment_id = Column(Integer, ForeignKey("target_segments.target_segment_id"), nullable=False)
    vr_popularity = Column(Numeric(5, 2), nullable=True)
    tpr_power_score = Column(Numeric(5, 2), nullable=True)
    base_power_score = Column(Numeric(5, 2), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # リレーション
    talent = relationship("Talent", back_populates="talent_scores")
    target_segment = relationship("TargetSegment")

    # 複合ユニーク制約とインデックス
    __table_args__ = (
        Index("idx_talent_scores_lookup", "target_segment_id", "base_power_score", unique=False),
        Index("idx_talent_scores_account", "account_id"),
        Index("idx_talent_scores_unique", "account_id", "target_segment_id", unique=True),
    )

    def __repr__(self):
        return f"<TalentScore(account_id={self.account_id}, target_segment_id={self.target_segment_id})>"


class TalentImage(Base):
    """タレントイメージスコアテーブル（VRイメージデータ、requirements.md準拠）"""
    __tablename__ = "talent_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("m_account.account_id", ondelete="CASCADE"), nullable=False)
    target_segment_id = Column(Integer, ForeignKey("target_segments.target_segment_id"), nullable=False)
    image_item_id = Column(Integer, ForeignKey("image_items.id"), nullable=False)
    score = Column(Numeric(5, 2), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # リレーション
    talent = relationship("Talent", back_populates="talent_images")
    target_segment = relationship("TargetSegment")
    image_item = relationship("ImageItem")

    # 複合ユニーク制約とインデックス
    __table_args__ = (
        Index("idx_talent_images_lookup", "target_segment_id", "image_item_id", "score"),
        Index("idx_talent_images_account", "account_id"),
        Index("idx_talent_images_unique", "account_id", "target_segment_id", "image_item_id", unique=True),
    )

    def __repr__(self):
        return f"<TalentImage(account_id={self.account_id}, image_item_id={self.image_item_id})>"


class MTalentCm(Base):
    """CM出演履歴テーブル（実際のm_talent_cmテーブルと対応）"""
    __tablename__ = "m_talent_cm"

    # 複合主キー（実際のDB構造に合わせる）
    account_id = Column(Integer, ForeignKey("m_account.account_id", ondelete="CASCADE"), primary_key=True)
    sub_id = Column(Integer, primary_key=True)

    # CM基本情報
    client_name = Column(String, nullable=True, comment="クライアント/スポンサー名")
    product_name = Column(String, nullable=True, comment="商品/サービス名（12%がNULL）")
    use_period_start = Column(String, nullable=True, comment="放映開始日 (YYYY-MM-DD形式)")
    use_period_end = Column(String, nullable=True, comment="放映終了日 (YYYY-MM-DD形式)")

    # 競合カテゴリコード
    rival_category_type_cd1 = Column(Integer, nullable=True, comment="競合カテゴリコード1")
    rival_category_type_cd2 = Column(Integer, nullable=True, comment="競合カテゴリコード2")
    rival_category_type_cd3 = Column(Integer, nullable=True, comment="競合カテゴリコード3")
    rival_category_type_cd4 = Column(Integer, nullable=True, comment="競合カテゴリコード4")

    # 制作関連情報（稀少データ）
    agency_name = Column(String, nullable=True, comment="代理店名（0.7%のみ有値）")
    production_name = Column(String, nullable=True, comment="制作会社名（0.7%のみ有値）")
    director = Column(String, nullable=True, comment="監督/演出名（0.5%のみ有値）")

    # その他
    note = Column(Text, nullable=True, comment="備考・契約状況等（98.4%有値）")
    regist_date = Column(DateTime, nullable=True, comment="登録日時")

    # リレーション
    talent = relationship("Talent", back_populates="cm_history")

    # インデックス
    __table_args__ = (
        Index("idx_m_talent_cm_account", "account_id"),
        Index("idx_m_talent_cm_client", "client_name"),
        Index("idx_m_talent_cm_period", "use_period_start", "use_period_end"),
    )

    def __repr__(self):
        return f"<TalentCmHistory(account_id={self.account_id}, client_name='{self.client_name}')>"


class FormSubmission(Base):
    """フォーム送信履歴テーブル"""
    __tablename__ = "form_submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, unique=True, index=True)
    industry = Column(String(100), nullable=False)
    target_segment = Column(String(50), nullable=False)
    purpose = Column(String(255), nullable=True)  # 起用目的
    budget_range = Column(String(100), nullable=False)
    company_name = Column(String(255), nullable=True)
    contact_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    genre_preference = Column(String(50), nullable=True)  # "はい"/"いいえ"
    preferred_genres = Column(Text, nullable=True)  # JSON文字列として複数ジャンルを保存
    email_consent = Column(Boolean, nullable=False, default=False)  # メール送信同意（特定電子メール法対応）
    email_consent_timestamp = Column(DateTime, nullable=True)  # メール送信同意日時
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # リレーション
    button_clicks = relationship("ButtonClick", back_populates="form_submission", cascade="all, delete-orphan")

    # インデックス
    __table_args__ = (
        Index("idx_form_submissions_created_at", "created_at"),
        Index("idx_form_submissions_session", "session_id"),
        Index("idx_form_submissions_industry", "industry"),
    )

    def __repr__(self):
        return f"<FormSubmission(id={self.id}, session_id='{self.session_id}', company_name='{self.company_name}')>"


class ButtonClick(Base):
    """ボタンクリック追跡テーブル"""
    __tablename__ = "button_clicks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    form_submission_id = Column(Integer, ForeignKey("form_submissions.id", ondelete="CASCADE"), nullable=False)
    button_type = Column(String(50), nullable=False)  # 'counseling_booking', 'download', etc.
    button_text = Column(String(255), nullable=True)
    clicked_at = Column(DateTime, server_default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # リレーション
    form_submission = relationship("FormSubmission", back_populates="button_clicks")

    # インデックス
    __table_args__ = (
        Index("idx_button_clicks_submission", "form_submission_id"),
        Index("idx_button_clicks_type", "button_type"),
        Index("idx_button_clicks_clicked_at", "clicked_at"),
    )

    def __repr__(self):
        return f"<ButtonClick(id={self.id}, form_submission_id={self.form_submission_id}, button_type='{self.button_type}')>"


class DiagnosisResult(Base):
    """診断結果タレント30名保存テーブル"""
    __tablename__ = "diagnosis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    form_submission_id = Column(Integer, ForeignKey("form_submissions.id", ondelete="CASCADE"), nullable=False)
    ranking = Column(Integer, nullable=False)
    talent_account_id = Column(Integer, nullable=False)
    talent_name = Column(String(255), nullable=False)
    talent_category = Column(String(255), nullable=True)
    matching_score = Column(Numeric(5, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # リレーション
    form_submission = relationship("FormSubmission", backref="diagnosis_results")

    # インデックス
    __table_args__ = (
        Index("idx_diagnosis_results_submission_id", "form_submission_id"),
        Index("idx_diagnosis_results_ranking", "form_submission_id", "ranking"),
    )

    def __repr__(self):
        return f"<DiagnosisResult(id={self.id}, form_submission_id={self.form_submission_id}, ranking={self.ranking}, talent_name='{self.talent_name}')>"


class RecommendedTalent(Base):
    """おすすめタレント設定テーブル（業界別）"""
    __tablename__ = "recommended_talents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    industry_name = Column(String(100), ForeignKey("industries.industry_name"), nullable=False)
    talent_id_1 = Column(Integer, ForeignKey("m_account.account_id"), nullable=True)  # 1番目のおすすめタレント
    talent_id_2 = Column(Integer, ForeignKey("m_account.account_id"), nullable=True)  # 2番目のおすすめタレント
    talent_id_3 = Column(Integer, ForeignKey("m_account.account_id"), nullable=True)  # 3番目のおすすめタレント
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション
    industry = relationship("Industry")
    talent_1 = relationship("Talent", foreign_keys=[talent_id_1])
    talent_2 = relationship("Talent", foreign_keys=[talent_id_2])
    talent_3 = relationship("Talent", foreign_keys=[talent_id_3])

    # インデックス
    __table_args__ = (
        Index("idx_recommended_talents_industry", "industry_name", unique=True),
    )

    def __repr__(self):
        return f"<RecommendedTalent(industry_name='{self.industry_name}', talent_ids=[{self.talent_id_1}, {self.talent_id_2}, {self.talent_id_3}])>"


class TalentSNSFollowers(Base):
    """SNSフォロワー数テーブル（Instagram、TikTok、X、YouTube）"""
    __tablename__ = "talent_sns_followers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("m_account.account_id", ondelete="CASCADE"), unique=True, nullable=False)
    x_followers = Column(Integer, nullable=True, comment="Xフォロワー数")
    instagram_followers = Column(Integer, nullable=True, comment="Instagramフォロワー数")
    tiktok_followers = Column(Integer, nullable=True, comment="TikTokフォロワー数")
    youtube_followers = Column(Integer, nullable=True, comment="YouTube登録者数")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # リレーションシップ
    talent = relationship("Talent", backref="sns_followers")

    # インデックス
    __table_args__ = (
        Index("idx_talent_sns_account", "account_id", unique=True),
        Index("idx_talent_sns_updated", "updated_at"),
    )

    def __repr__(self):
        return f"<TalentSNSFollowers(account_id={self.account_id}, x={self.x_followers}, ig={self.instagram_followers}, tiktok={self.tiktok_followers}, yt={self.youtube_followers})>"


class BookingLinkPattern(Base):
    """パターン別予約リンク管理テーブル（3パターンCTAリンク設定システム）"""
    __tablename__ = "booking_link_patterns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_key = Column(String(50), unique=True, nullable=False, comment="パターン識別子（high_budget/low_budget_influencer/low_budget_other）")
    pattern_name = Column(String(100), nullable=False, comment="パターン名（日本語表示用）")
    description = Column(Text, nullable=True, comment="パターン説明")
    booking_url = Column(Text, nullable=False, comment="予約ページURL")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    # インデックス
    __table_args__ = (
        Index("idx_booking_link_pattern_key", "pattern_key", unique=True),
    )

    def __repr__(self):
        return f"<BookingLinkPattern(pattern_key='{self.pattern_key}', pattern_name='{self.pattern_name}')>"
