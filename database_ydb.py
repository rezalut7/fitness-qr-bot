import os, ydb, ydb.iam
from datetime import datetime
from functools import partial

driver = ydb.Driver(
    ydb.DriverConfig(
        endpoint=os.getenv("YDB_ENDPOINT"),
        database=os.getenv("YDB_DATABASE"),
        credentials=ydb.iam.ServiceAccountCredentials(
            service_account_id=os.getenv("YDB_SA_ID"),
            private_key=os.getenv("YDB_SA_KEY"),
        ),
    )
)
driver.wait(fail_fast=True, timeout=10)
table_client = driver.table_client
session = table_client.session().create()

session.create_table(
    "/client",
    ydb.TableDescription()
    .with_primary_key("tg_id")
    .with_columns(
        ydb.Column("tg_id", ydb.OptionalType(ydb.PrimitiveType.Uint64)),
        ydb.Column("full_name", ydb.OptionalType(ydb.PrimitiveType.UTF8)),
        ydb.Column("phone", ydb.OptionalType(ydb.PrimitiveType.UTF8)),
        ydb.Column("consent_at", ydb.OptionalType(ydb.PrimitiveType.Timestamp)),
        ydb.Column("registered_at", ydb.OptionalType(ydb.PrimitiveType.Timestamp)),
    ),
    on_exist=ydb.OnTableExistPolicy.IGNORE,
)

def save_client(tg_id: int, full_name: str, phone: str, consent_at: datetime):
    def tx(sess):
        sess.transaction().execute(
            """
            UPSERT INTO client
            (tg_id, full_name, phone, consent_at, registered_at)
            VALUES ($id,$name,$phone,$consent,CurrentUtcTimestamp())
            """,
            {
                "$id": tg_id,
                "$name": full_name,
                "$phone": phone,
                "$consent": consent_at,
            },
            commit_tx=True,
        )
    table_client.retry_operation_sync(partial(tx))
