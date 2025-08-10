"""
Pricing and cost calculation functions for OpenRouter CLI.
Handles model pricing information and session cost calculations.
"""

from models_core import get_enhanced_models


def get_model_pricing_info(model_name):
    """Get pricing information for a specific model"""
    try:
        enhanced_models = get_enhanced_models()
        
        for model in enhanced_models:
            if model is None:
                continue
                
            # Check if this is the selected model
            model_slug = model.get('slug') or model.get('name') or model.get('short_name', '')
            if model_slug == model_name:
                endpoint = model.get('endpoint', {})
                if endpoint:
                    api_is_free = endpoint.get('is_free', False)
                    pricing = endpoint.get('pricing', {})
                    
                    # Check if the model name explicitly indicates it's free
                    is_explicitly_free = model_name and (model_name.endswith(':free') or ':free' in model_name)
                    
                    # Only trust is_free flag if the model name explicitly indicates it's free
                    # This prevents cases where the API incorrectly marks paid models as free
                    if is_explicitly_free and api_is_free:
                        return {
                            'is_free': True,
                            'prompt_price': 0.0,
                            'completion_price': 0.0,
                            'display': 'FREE',
                            'provider': endpoint.get('provider_name', 'Unknown')
                        }
                    elif pricing:
                        # Note: this is price per 1k tokens
                        prompt_price = float(pricing.get('prompt', '0')) * 1000
                        completion_price = float(pricing.get('completion', '0')) * 1000
                        
                        # Check if the model name explicitly indicates it's free
                        is_explicitly_free = model_name and (model_name.endswith(':free') or ':free' in model_name)
                        
                        if prompt_price == 0 and completion_price == 0:
                            if is_explicitly_free:
                                return {
                                    'is_free': True,
                                    'prompt_price': 0.0,
                                    'completion_price': 0.0,
                                    'display': 'FREE',
                                    'provider': endpoint.get('provider_name', 'Unknown')
                                }
                            else:
                                # Model has 0 pricing but may still require credits
                                # Don't trust 0-pricing for non-explicit free models
                                return {
                                    'is_free': False,
                                    'prompt_price': 0.0,
                                    'completion_price': 0.0,
                                    'display': 'Requires credits',
                                    'provider': endpoint.get('provider_name', 'Unknown')
                                }
                        else:
                            # Format prices for display
                            if prompt_price < 0.001:
                                prompt_display = f"${prompt_price:.4f}"
                            else:
                                prompt_display = f"${prompt_price:.3f}"
                                
                            if completion_price < 0.001:
                                completion_display = f"${completion_price:.4f}"
                            else:
                                completion_display = f"${completion_price:.3f}"
                                
                            return {
                                'is_free': False,
                                'prompt_price': prompt_price,
                                'completion_price': completion_price,
                                'display': f"{prompt_display}/1K prompt, {completion_display}/1K completion",
                                'provider': endpoint.get('provider_name', 'Unknown')
                            }
        
        # Model not found in enhanced models - check if it's a free model by name
        if model_name and (model_name.endswith(':free') or ':free' in model_name):
            return {
                'is_free': True,
                'prompt_price': 0.0,
                'completion_price': 0.0,
                'display': 'FREE',
                'provider': 'OpenRouter'
            }
        
        # Model not found in enhanced models and not obviously free
        return {
            'is_free': False,
            'prompt_price': 0.0,
            'completion_price': 0.0,
            'display': 'Pricing unknown - may require credits',
            'provider': 'Unknown'
        }
        
    except Exception as e:
        return {
            'is_free': False,
            'prompt_price': 0.0,
            'completion_price': 0.0,
            'display': 'Pricing unknown - may require credits',
            'provider': 'Unknown'
        }


def calculate_session_cost(total_prompt_tokens, total_completion_tokens, pricing_info):
    """Calculate the total cost for the current session"""
    if pricing_info['is_free']:
        return 0.0
    
    # Convert to cost per 1000 tokens
    prompt_cost = total_prompt_tokens * pricing_info['prompt_price']
    completion_cost = total_completion_tokens * pricing_info['completion_price']
    
    return prompt_cost + completion_cost
