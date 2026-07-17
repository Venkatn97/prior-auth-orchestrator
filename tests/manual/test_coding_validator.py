from agents.cluster_b.coding_validator import coding_validator_node

state = {
    'request_id': 'test-cb-3',
    'patient_ref': 'patient_002',
    'procedure_requested': 'MRI',
    'diagnosis_code': 'M54.5',
    'urgency': 'routine',
    'eligibility': {'found': True, 'eligible': False, 'plan': 'HMO Basic', 'coverage_percent': 0},
    'policy_match': None,
    'documentation_status': None,
    'coding_valid': None,
    'coding_notes': None,
    'errors': [],
}

result = coding_validator_node(state)
print(result['coding_valid'], '-', result['coding_notes'])
