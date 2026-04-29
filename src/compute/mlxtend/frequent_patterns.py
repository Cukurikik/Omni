"""
OMNI Compute Layer: MLxtend Apriori Frequent Patterns
Data mining algorithm for association rule learning.
"""
from typing import List, Tuple, Set, Dict, Optional
import itertools

Result = Tuple[Optional[List[Dict]], Optional[Exception]]

class AprioriEngine:
    def __init__(self, min_support: float = 0.1):
        self.min_support = min_support

    def _get_frequent_itemsets(self, transactions: List[Set[str]], itemsets: Set[Tuple[str, ...]]) -> Dict[Tuple[str, ...], float]:
        counts = {itemset: 0 for itemset in itemsets}
        num_transactions = len(transactions)
        
        for tx in transactions:
            for itemset in itemsets:
                if set(itemset).issubset(tx):
                    counts[itemset] += 1
                    
        frequent = {}
        for itemset, count in counts.items():
            support = count / num_transactions
            if support >= self.min_support:
                frequent[itemset] = support
        return frequent

    def fit(self, transactions_list: List[List[str]]) -> Result:
        try:
            transactions = [set(t) for t in transactions_list]
            
            # Step 1: 1-itemsets
            all_items = set(item for tx in transactions for item in tx)
            current_itemsets = {tuple([item]) for item in all_items}
            
            final_frequent_itemsets = []
            
            while current_itemsets:
                frequent = self._get_frequent_itemsets(transactions, current_itemsets)
                if not frequent:
                    break
                    
                for itemset, support in frequent.items():
                    final_frequent_itemsets.append({
                        "itemset": itemset,
                        "support": support
                    })
                
                # Generate candidates of length K+1
                items = list(set(i for itemset in frequent.keys() for i in itemset))
                k = len(list(frequent.keys())[0]) + 1
                current_itemsets = set(itertools.combinations(items, k))
                
            return final_frequent_itemsets, None
            
        except Exception as e:
            return None, e
