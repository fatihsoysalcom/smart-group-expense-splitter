import json

def calculate_group_expenses(transactions):
    """Calculates group expenses, accounting for non-drinkers."""
    # Initialize balances for each person
    balances = {} 
    for transaction in transactions:
        payer = transaction['payer']
        amount = transaction['amount']
        items = transaction['items']

        # Ensure payer is in balances, initialize to 0 if not
        balances.setdefault(payer, 0)

        # Calculate cost per person for this transaction
        total_items_cost = sum(item['price'] for item in items)
        num_people_sharing = len(set(person for item in items for person in item['shared_by']))
        
        # Determine who is actually paying for what, considering non-drinkers
        for item in items:
            item_price = item['price']
            shared_by = item['shared_by']
            
            # If the item is alcoholic and a person is marked as a non-drinker, they don't pay for it.
            # For simplicity, we assume 'alcoholic' is a property of the item.
            # In a real app, this would be more nuanced.
            actual_payers_for_item = []
            for person in shared_by:
                is_non_drinker = any(t['payer'] == person and t['type'] == 'non_drinker' for t in transactions if t['payer'] == person)
                if not (item.get('alcoholic', False) and is_non_drinker):
                    actual_payers_for_item.append(person)
            
            if actual_payers_for_item:
                cost_per_actual_payer = item_price / len(actual_payers_for_item)
                for person in actual_payers_for_item:
                    balances.setdefault(person, 0)
                    balances[person] -= cost_per_per_payer
                    balances[payer] += cost_per_per_payer
            else:
                # If no one can pay for this item (e.g., all drinkers left), the payer covers it.
                balances[payer] += item_price

    # Settle debts: find who owes whom
    debtors = {person: bal for person, bal in balances.items() if bal < 0}
    creditors = {person: bal for person, bal in balances.items() if bal > 0}

    settlements = []
    for debtor, debt_amount in debtors.items():
        debt_amount = abs(debt_amount)
        for creditor, credit_amount in creditors.items():
            if debt_amount <= 0: break
            transfer_amount = min(debt_amount, credit_amount)
            settlements.append({
                'from': debtor,
                'to': creditor,
                'amount': round(transfer_amount, 2)
            })
            debt_amount -= transfer_amount
            creditors[creditor] -= transfer_amount
            if creditors[creditor] == 0: del creditors[creditor]

    return balances, settlements

if __name__ == "__main__":
    # Example Usage:
    # Transactions include payer, amount, items, and potentially a 'type' for special roles like 'non_drinker'
    # Items have a price and a list of people they are shared by.
    # 'alcoholic': True indicates an alcoholic beverage.
    example_transactions = [
        {
            'payer': 'Alice',
            'amount': 50.0,
            'items': [
                {'name': 'Salad', 'price': 15.0, 'shared_by': ['Alice', 'Bob', 'Charlie']},
                {'name': 'Beer', 'price': 10.0, 'alcoholic': True, 'shared_by': ['Alice', 'Bob']},
                {'name': 'Wine', 'price': 25.0, 'alcoholic': True, 'shared_by': ['Alice', 'Charlie']}
            ]
        },
        {
            'payer': 'Bob',
            'amount': 30.0,
            'items': [
                {'name': 'Burger', 'price': 15.0, 'shared_by': ['Bob', 'Charlie']},
                {'name': 'Soda', 'price': 5.0, 'shared_by': ['Bob', 'Charlie', 'Alice']}
            ]
        },
        {
            'payer': 'Charlie',
            'amount': 0.0, # Charlie didn't pay for anything directly, but might owe
            'type': 'non_drinker' # Explicitly marking Charlie as a non-drinker
        }
    ]

    final_balances, settlement_plan = calculate_group_expenses(example_transactions)

    print("--- Final Balances ---")
    for person, balance in final_balances.items():
        print(f"{person}: {balance:.2f}")

    print("\n--- Settlement Plan ---")
    if settlement_plan:
        for settlement in settlement_plan:
            print(f"{settlement['from']} pays {settlement['to']} ${settlement['amount']}")
    else:
        print("No settlements needed.")
