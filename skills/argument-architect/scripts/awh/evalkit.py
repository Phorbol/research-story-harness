"""Aggregate supplied manuscript annotations; never manufacture semantic labels."""

from .contracts import ContractError

TRACKS = ('published_reconstruction', 'messy_materials', 'incremental_revision',
          'fault_injection', 'cross_domain', 'author_use')
RATIOS = {
    'key_claim_support': ('supported_key_claims', 'checked_key_claims'),
    'necessary_content_coverage': ('present_required_items', 'required_items'),
    'citation_existence': ('existing_citations', 'cited_references'),
    'citation_support': ('supporting_citations', 'checked_citations'),
    'citation_coverage': ('covered_claims', 'citation_needed_claims'),
    'review_issue_precision': ('valid_raised_issues', 'raised_issues'),
    'erroneous_revision_rate': ('erroneous_accepted_patches', 'accepted_patches'),
}


def summarize(rows):
    if not isinstance(rows, list) or not rows:
        raise ContractError('Supply nonempty, externally annotated manuscript records')
    seen = set()
    outputs = []
    for row in rows:
        required = {'paper_id', 'track', 'condition', 'stage', 'model', 'budget', 'materials_id',
                    'annotation_origin', 'counts', 'serious_scientific_errors', 'author_minutes'}
        if not isinstance(row, dict) or set(row) != required:
            raise ContractError('Evaluation row fields must be: ' + ', '.join(sorted(required)))
        if row['track'] not in TRACKS or row['stage'] not in ('story', 'realization'):
            raise ContractError('Unknown evaluation track or stage')
        if any(not isinstance(row[k], str) or not row[k].strip() for k in required -
               {'counts', 'serious_scientific_errors', 'author_minutes'}):
            raise ContractError('Evaluation identity/configuration fields must be nonempty strings')
        key = (row['paper_id'], row['track'], row['condition'], row['stage'])
        if key in seen:
            raise ContractError('Repeated ratings of the same manuscript condition are not independent papers')
        seen.add(key)
        counts = row['counts']
        fields = {field for pair in RATIOS.values() for field in pair}
        if not isinstance(counts, dict) or set(counts) != fields:
            raise ContractError('Evaluation counts must contain every declared numerator and denominator')
        if any(type(value) is not int or value < 0 for value in counts.values()):
            raise ContractError('Evaluation counts must be nonnegative integers')
        metrics = {}
        for name, (numerator, denominator) in RATIOS.items():
            if counts[numerator] > counts[denominator]:
                raise ContractError('Numerator exceeds denominator: ' + name)
            metrics[name] = counts[numerator] / counts[denominator] if counts[denominator] else None
        if type(row['serious_scientific_errors']) is not int or row['serious_scientific_errors'] < 0:
            raise ContractError('Serious scientific errors must be a nonnegative count')
        minutes = row['author_minutes']
        if type(minutes) not in (int, float) or minutes < 0:
            raise ContractError('Author minutes must be nonnegative')
        outputs.append({**row, 'metrics': metrics})
    return {'independent_paper_ids': len({row['paper_id'] for row in rows}), 'rows': outputs,
        'interpretation': 'Descriptive supplied annotations. No automatic quality labels, significance or causal gain claim.',
        'comparison_requirements': 'For 2x2 ablation fix materials, model, budget and stage; realization also fixes the approved plan.'}
