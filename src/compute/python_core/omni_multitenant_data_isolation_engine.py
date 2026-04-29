"""OmniMultitenantDataIsolationEngine — Column Discriminator Multitenancy.

Inspired by filipefox/spring-multitenancy-column-discriminator: a
Spring Boot base project for multitenancy using column discriminators
(Spring Data JPA with Hibernate).

Algorithmic Primitive:
    Enforce data isolation across multiple tenants residing in a single
    shared database structure. Apply tenant-identifier discrimination
    to filter read queries and automatically inject the tenant context
    into write/upsert operations.
"""
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from __future__ import annotations
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniMultitenantDataIsolationEngine:
    """Production-grade multitenancy data isolation engine."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniMultitenantDataIsolationEngine",
            "version": "1.0.0",
            "primitive": "column_discriminator_tenant_isolation",
            "monadic_enforcement": True,
            "source_repo": "filipefox/spring-multitenancy-column-discriminator",
        }

    @staticmethod
    def filter_by_tenant(
        records: list[dict],
        tenant_id: str,
        discriminator_column: str = "tenant_id",
    ) -> Result:
        """Filter a collection of records to only those matching the tenant context.

        Args:
            records: List of dictionaries representing database rows.
            tenant_id: The identifier of the active tenant.
            discriminator_column: The key used to identify the tenant ownership.

        Returns:
            Result[list[dict], Exception]: Filtered list of records.
        """
        if not isinstance(records, list):
            return Err(Exception("records must be a list"))
        if not tenant_id:
            return Err(Exception("tenant_id must be provided"))

        isolated_data: list[dict] = []
        for record in records:
            if not isinstance(record, dict):
                return Err(Exception("Each record must be a dict"))
            
            # Enforce strict isolation: drop records missing the discriminator entirely
            if discriminator_column not in record:
                continue
                
            if record[discriminator_column] == tenant_id:
                isolated_data.append(record)

        return Ok(isolated_data)

    @staticmethod
    def inject_tenant_context(
        records: list[dict],
        tenant_id: str,
        discriminator_column: str = "tenant_id",
        override_existing: bool = False,
    ) -> Result:
        """Inject tenant identifiers into records before writing/persistence.

        Args:
            records: List of dictionaries representing proposed database rows.
            tenant_id: The identifier of the active tenant.
            discriminator_column: The key used to identify the tenant ownership.
            override_existing: If False, throws an error if a tenant ID exists but differs.

        Returns:
            Result[list[dict], Exception]: Mutated list of records with tenant injected.
        """
        if not isinstance(records, list):
            return Err(Exception("records must be a list"))
        if not tenant_id:
            return Err(Exception("tenant_id must be provided"))

        processed_records: list[dict] = []
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                return Err(Exception("Each record must be a dict"))
            
            new_record = record.copy()
            existing_tenant = new_record.get(discriminator_column)

            if existing_tenant is not None and existing_tenant != tenant_id:
                if not override_existing:
                    return Err(Exception(f"Cross-tenant pollution detected at index {index}. Expected '{tenant_id}', got '{existing_tenant}'."))
                
            new_record[discriminator_column] = tenant_id
            processed_records.append(new_record)

        return Ok(processed_records)
