"""SQLAlchemyモデル定義（単一真実源の原則）"""
from sqlalchemy import Column, Integer, String, ForeignKey, Index, DateTime, Numeric, Date
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Industry(Base):
    """業種マスタテーブル（CLAUDE.md + requirements.md準拠）"""
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    display_order = Column(Integer, default=0)

    # リレーション
    industry_images = relationship("IndustryImage", back_populates="industry")

    def __repr__(self):
        return f"<Industry(id={self.id}, name='{self.name}')>"


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
    industry_id = Column(Integer, ForeignKey("industries.id", ondelete="CASCADE"), nullable=False)
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
    image_file_name = Column(String(255), nullable=True)
    pref = Column(Integer, nullable=True)
    url = Column(String(1000), nullable=True)
    del_flag = Column(Integer, default=0, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション（talent_scores/talent_imagesは account_id で参照）
    talent_scores = relationship("TalentScore", back_populates="talent", cascade="all, delete-orphan", foreign_keys="TalentScore.account_id")
    talent_images = relationship("TalentImage", back_populates="talent", cascade="all, delete-orphan", foreign_keys="TalentImage.account_id")
    talent_act = relationship("TalentAct", back_populates="account", uselist=False)

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


class TalentCmHistory(Base):
    """CM出演履歴テーブル"""
    __tablename__ = "talent_cm_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("m_account.account_id", ondelete="CASCADE"), nullable=False)
    sub_id = Column(Integer, nullable=False)
    client_name = Column(String(255), nullable=True)
    product_name = Column(String(255), nullable=True)
    use_period_start = Column(Date, nullable=True)
    use_period_end = Column(Date, nullable=True)
    rival_category_type_cd1 = Column(Integer, nullable=True)
    rival_category_type_cd2 = Column(Integer, nullable=True)
    rival_category_type_cd3 = Column(Integer, nullable=True)
    rival_category_type_cd4 = Column(Integer, nullable=True)
    note = Column(String, nullable=True)
    regist_date = Column(DateTime, nullable=True)
    up_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション
    talent = relationship("Talent")

    # インデックス
    __table_args__ = (
        Index("idx_cm_account_id", "account_id"),
        Index("idx_cm_client", "client_name"),
        Index("idx_cm_period", "use_period_start", "use_period_end"),
    )

    def __repr__(self):
        return f"<TalentCmHistory(account_id={self.account_id}, client_name='{self.client_name}')>"
