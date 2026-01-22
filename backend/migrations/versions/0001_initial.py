"""Initial migration

Revision ID: 0001_initial
Revises:
Create Date: 2024-01-22 15:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # Create properties table
    op.create_table(
        "properties",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("lot_number", sa.String(length=10), nullable=True),
        sa.Column("block_number", sa.String(length=10), nullable=True),
        sa.Column("zip_code", sa.String(length=10), nullable=True),
        sa.Column("building_area_sf", sa.Float(), nullable=True),
        sa.Column("land_area_sf", sa.Float(), nullable=False),
        sa.Column("current_use", sa.String(length=100), nullable=True),
        sa.Column("geom", geoalchemy2.Geometry("POINT", srid=4326), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_properties_id"), "properties", ["id"], unique=False)
    op.create_index(
        op.f("ix_properties_address"), "properties", ["address"], unique=False
    )
    op.create_index(
        "idx_properties_geom",
        "properties",
        ["geom"],
        unique=False,
        postgresql_using="gist",
    )

    # Create zoning_districts table
    op.create_table(
        "zoning_districts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("district_code", sa.String(length=20), nullable=False),
        sa.Column("district_name", sa.String(length=200), nullable=True),
        sa.Column("far_base", sa.Float(), nullable=False),
        sa.Column("far_with_bonus", sa.Float(), nullable=False),
        sa.Column("max_height_ft", sa.Float(), nullable=True),
        sa.Column(
            "setback_requirements",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("building_class", sa.String(length=10), nullable=True),
        sa.Column(
            "geom", geoalchemy2.Geometry("MULTIPOLYGON", srid=4326), nullable=True
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("district_code"),
    )
    op.create_index(
        op.f("ix_zoning_districts_id"), "zoning_districts", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_zoning_districts_district_code"),
        "zoning_districts",
        ["district_code"],
        unique=False,
    )
    op.create_index(
        "idx_zoning_districts_geom",
        "zoning_districts",
        ["geom"],
        unique=False,
        postgresql_using="gist",
    )

    # Create property_zoning table
    op.create_table(
        "property_zoning",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("zoning_district_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("percent_in_district", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["zoning_district_id"], ["zoning_districts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_property_zoning_property_id"),
        "property_zoning",
        ["property_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_property_zoning_zoning_district_id"),
        "property_zoning",
        ["zoning_district_id"],
        unique=False,
    )

    # Create landmarks table
    op.create_table(
        "landmarks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("landmark_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("geom", geoalchemy2.Geometry("POINT", srid=4326), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_landmarks_id"), "landmarks", ["id"], unique=False)
    op.create_index(op.f("ix_landmarks_name"), "landmarks", ["name"], unique=False)
    op.create_index(
        op.f("ix_landmarks_landmark_type"), "landmarks", ["landmark_type"], unique=False
    )
    op.create_index(
        "idx_landmarks_geom",
        "landmarks",
        ["geom"],
        unique=False,
        postgresql_using="gist",
    )

    # Create tax_incentive_programs table
    op.create_table(
        "tax_incentive_programs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("program_code", sa.String(length=20), nullable=False),
        sa.Column("program_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "eligible_zoning_districts",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("min_building_age", sa.Integer(), nullable=True),
        sa.Column("requires_residential", sa.Boolean(), nullable=True),
        sa.Column("tax_abatement_years", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("program_code"),
    )
    op.create_index(
        op.f("ix_tax_incentive_programs_id"),
        "tax_incentive_programs",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tax_incentive_programs_program_code"),
        "tax_incentive_programs",
        ["program_code"],
        unique=False,
    )

    # Create property_tax_incentives table
    op.create_table(
        "property_tax_incentives",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("program_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_eligible", sa.Boolean(), nullable=True),
        sa.Column("eligibility_reason", sa.Text(), nullable=True),
        sa.Column("estimated_abatement_value", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["program_id"], ["tax_incentive_programs.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_property_tax_incentives_program_id"),
        "property_tax_incentives",
        ["program_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_property_tax_incentives_property_id"),
        "property_tax_incentives",
        ["property_id"],
        unique=False,
    )

    # Create air_rights table
    op.create_table(
        "air_rights",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("unused_far", sa.Float(), nullable=False),
        sa.Column("transferable_far", sa.Float(), nullable=False),
        sa.Column("tdr_price_per_sf", sa.Float(), nullable=True),
        sa.Column(
            "adjacent_property_ids",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("property_id"),
    )
    op.create_index(op.f("ix_air_rights_id"), "air_rights", ["id"], unique=False)
    op.create_index(
        op.f("ix_air_rights_property_id"), "air_rights", ["property_id"], unique=True
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("air_rights")
    op.drop_table("property_tax_incentives")
    op.drop_table("tax_incentive_programs")
    op.drop_table("landmarks")
    op.drop_table("property_zoning")
    op.drop_table("zoning_districts")
    op.drop_table("properties")
