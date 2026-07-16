class TestFindByTransactionId:

    def test_returns_none_when_not_found(self, booking_repository, db_session):
        result = booking_repository.find_by_transaction_id(db_session, "nonexistent-id")
        assert result is None

    def test_returns_booking_when_found(self, booking_repository, db_session):
        records = [_build_record(transaction_id="txn-001")]
        booking_repository.bulk_save(db_session, records)
        db_session.flush()

        result = booking_repository.find_by_transaction_id(db_session, "txn-001")

        assert result is not None
        assert result.transaction_id == "txn-001"


class TestBulkSaveInsert:

    def test_inserts_new_records(self, booking_repository, db_session):
        records = [
            _build_record(transaction_id="txn-100"),
            _build_record(transaction_id="txn-101"),
        ]

        result = booking_repository.bulk_save(db_session, records)

        assert result == {"inserted": 2, "updated": 0}

    def test_inserted_record_has_correct_field_values(self, booking_repository, db_session):
        records = [_build_record(transaction_id="txn-200", status="pending", region="Asia")]
        booking_repository.bulk_save(db_session, records)
        db_session.flush()

        saved = booking_repository.find_by_transaction_id(db_session, "txn-200")

        assert saved.status == "pending"
        assert saved.region == "Asia"


class TestBulkSaveUpdate:

    def test_updates_existing_record_on_conflict(self, booking_repository, db_session):
        original = [_build_record(transaction_id="txn-300", status="pending")]
        booking_repository.bulk_save(db_session, original)
        db_session.flush()

        updated = [_build_record(transaction_id="txn-300", status="approved")]
        result = booking_repository.bulk_save(db_session, updated)
        db_session.flush()

        saved = booking_repository.find_by_transaction_id(db_session, "txn-300")

        assert result == {"inserted": 0, "updated": 1}
        assert saved.status == "approved"

    def test_mixed_batch_of_new_and_existing_records(self, booking_repository, db_session):
        booking_repository.bulk_save(db_session, [_build_record(transaction_id="txn-400")])
        db_session.flush()

        mixed_batch = [
            _build_record(transaction_id="txn-400", status="approved"),
            _build_record(transaction_id="txn-401", status="pending"),
        ]
        result = booking_repository.bulk_save(db_session, mixed_batch)

        assert result == {"inserted": 1, "updated": 1}


class TestBulkSaveChunking:

    def test_records_larger_than_chunk_size_are_all_saved(self, booking_repository, db_session):
        records = [_build_record(transaction_id=f"txn-bulk-{i}") for i in range(120)]

        result = booking_repository.bulk_save(db_session, records)

        assert result["inserted"] == 120
        assert result["updated"] == 0

    def test_empty_list_saves_nothing(self, booking_repository, db_session):
        result = booking_repository.bulk_save(db_session, [])
        assert result == {"inserted": 0, "updated": 0}


def _build_record(transaction_id, status="pending", region="Europe"):
    """Shared helper to build a minimal valid transformed booking record for repository tests."""
    return {
        "transaction_id": transaction_id,
        "conversion_key": "k-htl_d-m_p-BC-100",
        "property_id": "BC-100",
        "referral_property_id": "BC-100",
        "status": status,
        "travel_purpose": "leisure",
        "country_code": "DE",
        "region": region,
        "currency": "EUR",
        "check_in_date": "2026-09-15",
        "check_out_date": "2026-09-18",
        "site_key": "HTL",
        "device": "mobile",
        "total_price": 100.00,
        "revenue_usd": 108.00,
    }
