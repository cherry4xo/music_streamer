from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "uuid" UUID NOT NULL PRIMARY KEY,
    "username" VARCHAR(100) NOT NULL UNIQUE,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "recovery_email" VARCHAR(255),
    "first_name" VARCHAR(100) NOT NULL,
    "second_name" VARCHAR(100),
    "display_name" VARCHAR(100) NOT NULL,
    "status" VARCHAR(9) NOT NULL DEFAULT 'pending',
    "is_email_verified" BOOL NOT NULL DEFAULT False,
    "last_login" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "theme_preference" VARCHAR(6) NOT NULL DEFAULT 'system',
    "language_preference" VARCHAR(2) NOT NULL DEFAULT 'en',
    "email_notifications_enabled" BOOL NOT NULL DEFAULT True,
    "email_marketing_notifications_enabled" BOOL NOT NULL DEFAULT True,
    "push_notifications_enabled" BOOL NOT NULL DEFAULT True,
    "profile_visibility" VARCHAR(7) NOT NULL DEFAULT 'public',
    "activity_sharing_enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "edited_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_users_status_941fc1" ON "users" ("status");
CREATE INDEX IF NOT EXISTS "idx_users_theme_p_fabec4" ON "users" ("theme_preference");
CREATE INDEX IF NOT EXISTS "idx_users_languag_aa26dd" ON "users" ("language_preference");
CREATE INDEX IF NOT EXISTS "idx_users_profile_4cca32" ON "users" ("profile_visibility");
CREATE INDEX IF NOT EXISTS "idx_users_activit_9cace2" ON "users" ("activity_sharing_enabled");
COMMENT ON COLUMN "users"."status" IS 'PENDING: pending\nACTIVE: active\nINACTIVE: inactive\nSUSPENDED: suspended\nDELETED: deleted';
COMMENT ON COLUMN "users"."theme_preference" IS 'LIGHT: light\nDARK: dark\nSYSTEM: system';
COMMENT ON COLUMN "users"."language_preference" IS 'EN: en\nES: es';
COMMENT ON COLUMN "users"."profile_visibility" IS 'PUBLIC: public\nPRIVATE: private';
CREATE TABLE IF NOT EXISTS "account_activity_log" (
    "uuid" UUID NOT NULL PRIMARY KEY,
    "activity_type" VARCHAR(24) NOT NULL,
    "detail" JSONB,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actor_id" UUID,
    "actor_type" VARCHAR(6),
    "user_id" UUID NOT NULL REFERENCES "users" ("uuid") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_account_act_activit_6c1b99" ON "account_activity_log" ("activity_type");
COMMENT ON COLUMN "account_activity_log"."activity_type" IS 'EMAIL_UPDATED: email_updated\nUSERNAME_UPDATED: username_updated\nPROFILE_UPDATED: profile_updated\nSTATUS_CHANGED: status_changed\nPASSWORD_RESET_REQUESTED: password_reset_requested\nACCOUNT_CREATED: account_created\nACCOUNT_DELETED: account_deleted\nACCOUNT_SUSPENDED: account_suspended\nACCOUNT_REACTIVATED: account_reactivated';
COMMENT ON COLUMN "account_activity_log"."actor_type" IS 'USER: user\nADMIN: admin\nSYSTEM: system';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
