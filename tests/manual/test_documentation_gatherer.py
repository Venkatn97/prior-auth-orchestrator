from agents.cluster_b.documentation_gatherer import documentation_gatherer_node

state = {
    'request_id': 'test-cb-2',
    'patient_ref': 'patient_002',
    'procedure_requested': 'MRI',
    'diagnosis_code': 'M54.5',
    'urgency': 'routine',
    'eligibility': {'found': True, 'eligible': False, 'plan': 'HMO Basic', 'coverage_percent': 0},
    'policy_match': {
        'found': True,
        'requires_prior_auth': True,
        'criteria': 'Prior authorization required unless conservative treatment (physical therapy or medication) for at least 6 weeks has failed',
        'confidence': 'high',
    },
    'documentation_status': None,
    'coding_valid': None,
    'coding_notes': None,
    'errors': [],
}

result = documentation_gatherer_node(state)
print(result['documentation_status'])
