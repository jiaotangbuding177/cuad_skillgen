"""
Contract sampler for CUAD-SkillGen baselines.

Provides deterministic sampling of training contracts,
with priority given to contracts that have evidence for a specific case.
"""

import random
from typing import List, Optional, Set


class ContractSampler:
    """Deterministic contract sampler for baseline methods."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    def sample_contracts(
        self,
        all_contract_ids: List[str],
        n: int,
        priority_ids: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Sample n contracts from all_contract_ids.

        Contracts in priority_ids are selected first (shuffled among themselves).
        Remaining slots are filled from non-priority contracts (also shuffled).

        Args:
            all_contract_ids: All available contract IDs
            n: Number of contracts to sample
            priority_ids: Contract IDs to prioritize (e.g., those with evidence)

        Returns:
            List of sampled contract IDs (length <= n)
        """
        rng = random.Random(self.seed)

        if priority_ids is None:
            priority_ids = set()

        priority_list = [cid for cid in all_contract_ids if cid in priority_ids]
        non_priority_list = [cid for cid in all_contract_ids if cid not in priority_ids]

        rng.shuffle(priority_list)
        rng.shuffle(non_priority_list)

        # Take from priority first, then fill from non-priority
        sampled = priority_list[:n]
        remaining = n - len(sampled)
        if remaining > 0:
            sampled.extend(non_priority_list[:remaining])

        return sampled

    def sample_contracts_for_case(
        self,
        train_contract_ids: List[str],
        n: int,
        contracts_with_evidence: Set[str],
    ) -> List[str]:
        """
        Sample n training contracts for a specific case.

        Prioritizes contracts that have evidence units for this case.

        Args:
            train_contract_ids: All train split contract IDs
            n: Number to sample
            contracts_with_evidence: Contract IDs with evidence for this case

        Returns:
            List of sampled contract IDs
        """
        return self.sample_contracts(
            all_contract_ids=train_contract_ids,
            n=n,
            priority_ids=contracts_with_evidence,
        )
