from rich.console import Console
from rich.prompt import Prompt

# Import required functions from other modules
from models_core import get_available_models
from models_filtering import get_dynamic_task_categories, get_models_by_capability, get_models_by_group

# Initialize Rich console
console = Console()

# Check for FZF availability
try:
    from fzf import FzfPrompt
    HAS_FZF = True
except ImportError:
    HAS_FZF = False

def auto_detect_thinking_mode(config, selected_model):
    """Automatically detect if the selected model supports thinking mode"""
    # Make sure the thinking_mode key exists in config
    if 'thinking_mode' not in config:
        config['thinking_mode'] = False  # Default to disabled

    try:
        # Import here to avoid circular imports
        from models_core import get_enhanced_models
        
        # Get enhanced models to check if this model supports reasoning
        enhanced_models = get_enhanced_models()
        
        for model in enhanced_models:
            if model is None:
                continue
                
            # Check if this is the selected model
            model_slug = model.get('slug') or model.get('name') or model.get('short_name', '')
            if model_slug == selected_model:
                # Check if model supports reasoning/thinking
                endpoint = model.get('endpoint', {})
                supports_reasoning = endpoint.get('supports_reasoning', False) if endpoint else False
                reasoning_config = model.get('reasoning_config') or (endpoint.get('reasoning_config') if endpoint else None)
                
                if supports_reasoning or reasoning_config:
                    config['thinking_mode'] = True
                    console.print("[green]Thinking mode automatically enabled for this reasoning model.[/green]")
                    if reasoning_config:
                        start_token = reasoning_config.get('start_token', '<thinking>')
                        end_token = reasoning_config.get('end_token', '</thinking>')
                        console.print(f"[dim]Uses reasoning tags: {start_token}...{end_token}[/dim]")
                else:
                    config['thinking_mode'] = False
                    console.print("[dim]Thinking mode disabled - this model doesn't support reasoning.[/dim]")
                return
        
        # If model not found in enhanced models, disable thinking mode
        config['thinking_mode'] = False
        console.print("[dim]Thinking mode disabled - unable to verify reasoning support.[/dim]")
        
    except Exception as e:
        # If there's an error, keep current setting or default to disabled
        config['thinking_mode'] = config.get('thinking_mode', False)
        console.print(f"[yellow]Could not auto-detect thinking mode: {str(e)}[/yellow]")
        console.print(f"[dim]Keeping current setting: {'enabled' if config['thinking_mode'] else 'disabled'}[/dim]")


def select_model(config):
    """Simplified model selection interface"""
    all_models = get_available_models()

    if not all_models:
        console.print("[red]No models available. Please check your API key and internet connection.[/red]")
        return None

    # Option to directly enter a model name
    console.print("[bold green]Model Selection[/bold green]")
    console.print("\n[bold magenta]Options:[/bold magenta]")
    console.print("[bold]1[/bold] - View all available models")
    console.print("[bold]2[/bold] - Show free models only")
    console.print("[bold]3[/bold] - Enter model name directly")
    console.print("[bold]4[/bold] - Browse models by task category")
    console.print("[bold]5[/bold] - Browse by capabilities (enhanced)")
    console.print("[bold]6[/bold] - Browse by model groups")
    console.print("[bold]q[/bold] - Cancel selection")

    choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "q"], default="1")

    if choice == "q":
        return None

    elif choice == "3":
        # Direct model name entry
        console.print("[yellow]Enter the exact model name (e.g., 'anthropic/claude-3-opus')[/yellow]")
        model_name = Prompt.ask("Model name")

        # Validate the model name
        model_exists = any(model["id"] == model_name for model in all_models)
        if model_exists:
            # Auto-detect thinking mode support first
            try:
                auto_detect_thinking_mode(config, model_name)
            except Exception as e:
                console.print(f"[yellow]Error auto-detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
            return model_name

        console.print("[yellow]Warning: Model not found in available models. Using anyway.[/yellow]")
        confirm = Prompt.ask("Continue with this model name? (y/n)", default="y")
        if confirm.lower() == "y":
            # Auto-detect thinking mode support first
            try:
                auto_detect_thinking_mode(config, model_name)
            except Exception as e:
                console.print(f"[yellow]Error auto-detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
            return model_name
        return select_model(config)  # Start over

    elif choice == "1":
        # All models, simple numbered list
        console.print("[bold green]All Available Models:[/bold green]")

        if HAS_FZF:
            try:
                fzf = FzfPrompt()
                model_choice = fzf.prompt([ model['id']  for  model in all_models ])
                if not model_choice:
                    console.print("[red]No model selected. Exiting...[/red]")
                    return select_model(config)
                else:
                    try:
                        auto_detect_thinking_mode(config, model_choice[0])
                    except Exception as e:
                        console.print(f"[yellow]Error auto-detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
                    return model_choice[0]
            except Exception as e:
                console.print(f"[yellow]FZF not available: {str(e)}. Falling back to numbered list.[/yellow]")
                # Fall through to the numbered list below

        with console.pager(styles=True):
            for i, model in enumerate(all_models, 1):
                # Highlight free models
                if model['id'].endswith(":free"):
                    console.print(f"[bold]{i}.[/bold] {model['id']} [green](FREE)[/green]")
                else:
                    console.print(f"[bold]{i}.[/bold] {model['id']}")

        model_choice = Prompt.ask("Enter model number or 'b' to go back", default="1")

        if model_choice.lower() == 'b':
            return select_model(config)

        try:
            index = int(model_choice) - 1
            if 0 <= index < len(all_models):
                selected_model = all_models[index]['id']
                # Auto-detect thinking mode support
                try:
                    auto_detect_thinking_mode(config, selected_model)
                except Exception as e:
                    console.print(f"[yellow]Error auto-detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
                return selected_model
            else:
                console.print("[red]Invalid selection[/red]")
                return select_model(config)
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
            return select_model(config)

    elif choice == "2":
        # Show only free models
        free_models = [model for model in all_models if model['id'].endswith(":free")]

        if not free_models:
            console.print("[yellow]No free models found.[/yellow]")
            Prompt.ask("Press Enter to continue")
            return select_model(config)

        console.print("[bold green]Free Models:[/bold green]")
        for i, model in enumerate(free_models, 1):
            console.print(f"[bold]{i}.[/bold] {model['id']} [green](FREE)[/green]")

        model_choice = Prompt.ask("Enter model number or 'b' to go back", default="1")

        if model_choice.lower() == 'b':
            return select_model(config)

        try:
            index = int(model_choice) - 1
            if 0 <= index < len(free_models):
                selected_model = free_models[index]['id']
                # Auto-detect thinking mode support
                try:
                    auto_detect_thinking_mode(config, selected_model)
                except Exception as e:
                    console.print(f"[yellow]Error auto-detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
                return selected_model
            console.print("[red]Invalid selection[/red]")
            Prompt.ask("Press Enter to continue")
            return select_model(config)
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
            Prompt.ask("Press Enter to continue")
            return select_model(config)

    elif choice == "4":
        # Browse models by task category using dynamic categories
        console.print("[bold green]Browse Models by Task Category:[/bold green]")
        console.print("[dim]Using dynamic categories from OpenRouter API[/dim]\n")
        
        # Available task categories
        task_categories = ["creative", "coding", "analysis", "chat"]
        
        console.print("[bold magenta]Available Categories:[/bold magenta]")
        for i, category in enumerate(task_categories, 1):
            console.print(f"[bold]{i}.[/bold] {category.title()}")
        console.print("[bold]b[/bold] - Go back to main menu")
        
        category_choice = Prompt.ask("Select a category", choices=["1", "2", "3", "4", "b"], default="1")
        
        if category_choice.lower() == 'b':
            return select_model(config)
        
        try:
            category_index = int(category_choice) - 1
            if 0 <= category_index < len(task_categories):
                selected_category = task_categories[category_index]
                
                # Get models for the selected category using dynamic categories
                console.print(f"[cyan]Loading {selected_category} models...[/cyan]")
                try:
                    dynamic_categories = get_dynamic_task_categories()
                    category_models = dynamic_categories.get(selected_category, [])
                    
                    if not category_models:
                        console.print(f"[yellow]No models found for {selected_category} category.[/yellow]")
                        Prompt.ask("Press Enter to continue")
                        return select_model(config)
                    
                    # Get full model details for display
                    all_models = get_available_models()
                    detailed_models = []
                    for model in all_models:
                        if model['id'] in category_models:
                            detailed_models.append(model)
                    
                    if not detailed_models:
                        console.print(f"[yellow]No detailed model information found for {selected_category} category.[/yellow]")
                        Prompt.ask("Press Enter to continue")
                        return select_model(config)
                    
                    console.print(f"[bold green]{selected_category.title()} Models:[/bold green]")
                    console.print(f"[dim]Found {len(detailed_models)} models optimized for {selected_category} tasks[/dim]\n")
                    
                    for i, model in enumerate(detailed_models, 1):
                        # Highlight free models and show pricing info
                        if model['id'].endswith(":free"):
                            console.print(f"[bold]{i}.[/bold] {model['id']} [green](FREE)[/green]")
                        else:
                            # Try to show pricing if available
                            pricing = ""
                            if 'pricing' in model and 'prompt' in model['pricing']:
                                try:
                                    prompt_price = float(model['pricing']['prompt'])
                                    if prompt_price > 0:
                                        pricing = f" [dim](${prompt_price:.6f}/token)[/dim]"
                                except:
                                    pass
                            console.print(f"[bold]{i}.[/bold] {model['id']}{pricing}")
                    
                    console.print(f"\n[bold]b[/bold] - Go back to category selection")
                    
                    model_choice = Prompt.ask("Enter model number or 'b' to go back", default="1")
                    
                    if model_choice.lower() == 'b':
                        return select_model(config)
                    
                    try:
                        model_index = int(model_choice) - 1
                        if 0 <= model_index < len(detailed_models):
                            selected_model = detailed_models[model_index]['id']
                            console.print(f"[green]Selected {selected_model} for {selected_category} tasks[/green]")
                            
                            # Auto-detect thinking mode support
                            try:
                                auto_detect_thinking_mode(config, selected_model)
                            except Exception as e:
                                console.print(f"[yellow]Error auto-detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
                            return selected_model
                        else:
                            console.print("[red]Invalid selection[/red]")
                            Prompt.ask("Press Enter to continue")
                            return select_model(config)
                    except ValueError:
                        console.print("[red]Please enter a valid number[/red]")
                        Prompt.ask("Press Enter to continue")
                        return select_model(config)
                        
                except Exception as e:
                    console.print(f"[red]Error loading dynamic categories: {str(e)}[/red]")
                    console.print("[yellow]Falling back to standard model selection[/yellow]")
                    Prompt.ask("Press Enter to continue")
                    return select_model(config)
            else:
                console.print("[red]Invalid category selection[/red]")
                return select_model(config)
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
            return select_model(config)

    elif choice == "5":
        # Browse models by capabilities using enhanced API
        console.print("[bold green]Browse Models by Capabilities:[/bold green]")
        console.print("[dim]Using enhanced OpenRouter frontend API data[/dim]\n")
        
        # Available capability filters
        capabilities = [
            ("reasoning", "Models with thinking/reasoning support"),
            ("multipart", "Models that support images and files"),
            ("tools", "Models with tool/function calling support"),
            ("free", "Free models (no cost)")
        ]
        
        console.print("[bold magenta]Available Capabilities:[/bold magenta]")
        for i, (cap, desc) in enumerate(capabilities, 1):
            console.print(f"[bold]{i}.[/bold] {desc}")
        console.print("[bold]b[/bold] - Go back to main menu")
        
        cap_choice = Prompt.ask("Select a capability", choices=["1", "2", "3", "4", "b"], default="1")
        
        if cap_choice.lower() == 'b':
            return select_model(config)
        
        try:
            cap_index = int(cap_choice) - 1
            if 0 <= cap_index < len(capabilities):
                selected_capability, description = capabilities[cap_index]
                
                # Get models with the selected capability
                console.print(f"[cyan]Loading models with {description.lower()}...[/cyan]")
                try:
                    capability_models = get_models_by_capability(selected_capability)
                    
                    if not capability_models:
                        console.print(f"[yellow]No models found with {description.lower()}.[/yellow]")
                        Prompt.ask("Press Enter to continue")
                        return select_model(config)
                    
                    console.print(f"[bold green]{description}:[/bold green]")
                    console.print(f"[dim]Found {len(capability_models)} models[/dim]\n")
                    
                    for i, model in enumerate(capability_models, 1):
                        # Skip None models in display
                        if model is None:
                            continue
                            
                        # Show enhanced model information
                        endpoint = model.get('endpoint', {}) if model else {}
                        # Try multiple fields for model name
                        model_name = model.get('slug') or model.get('name') or model.get('short_name', 'Unknown') if model else 'Unknown'
                        
                        # Show capability-specific information
                        extra_info = ""
                        if selected_capability == "reasoning":
                            reasoning_config = model.get('reasoning_config') or endpoint.get('reasoning_config') if model and endpoint else None
                            if reasoning_config:
                                start_token = reasoning_config.get('start_token', '<thinking>')
                                end_token = reasoning_config.get('end_token', '</thinking>')
                                extra_info = f" [dim]({start_token}...{end_token})[/dim]"
                        elif selected_capability == "multipart":
                            input_modalities = model.get('input_modalities', []) if model else []
                            if input_modalities:
                                extra_info = f" [dim]({', '.join(input_modalities)})[/dim]"
                        elif selected_capability == "tools":
                            supported_params = endpoint.get('supported_parameters', []) if endpoint else []
                            if supported_params is None:
                                supported_params = []
                            tool_params = [p for p in supported_params if 'tool' in p.lower()]
                            if tool_params:
                                extra_info = f" [dim]({', '.join(tool_params)})[/dim]"
                        elif selected_capability == "free":
                            provider = endpoint.get('provider_name', 'Unknown') if endpoint else 'Unknown'
                            extra_info = f" [green](FREE via {provider})[/green]"
                        
                        console.print(f"[bold]{i}.[/bold] {model_name}{extra_info}")
                    
                    console.print(f"\n[bold]b[/bold] - Go back to capability selection")
                    
                    model_choice = Prompt.ask("Enter model number or 'b' to go back", default="1")
                    
                    if model_choice.lower() == 'b':
                        return select_model(config)
                    
                    try:
                        model_index = int(model_choice) - 1
                        if 0 <= model_index < len(capability_models):
                            selected_model_obj = capability_models[model_index]
                            if selected_model_obj:
                                selected_model = selected_model_obj.get('slug') or selected_model_obj.get('name') or selected_model_obj.get('short_name', 'Unknown')
                            else:
                                selected_model = 'Unknown'
                            console.print(f"[green]Selected {selected_model} with {description.lower()}[/green]")
                            
                            # Auto-detect thinking mode support
                            try:
                                auto_detect_thinking_mode(config, selected_model)
                            except Exception as e:
                                console.print(f"[yellow]Error detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
                            return selected_model
                        else:
                            console.print("[red]Invalid selection[/red]")
                            Prompt.ask("Press Enter to continue")
                            return select_model(config)
                    except ValueError:
                        console.print("[red]Please enter a valid number[/red]")
                        Prompt.ask("Press Enter to continue")
                        return select_model(config)
                        
                except Exception as e:
                    console.print(f"[red]Error loading capability models: {str(e)}[/red]")
                    console.print("[yellow]Falling back to standard model selection[/yellow]")
                    Prompt.ask("Press Enter to continue")
                    return select_model(config)
            else:
                console.print("[red]Invalid capability selection[/red]")
                return select_model(config)
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
            return select_model(config)

    elif choice == "6":
        # Browse models by groups using enhanced API
        console.print("[bold green]Browse Models by Groups:[/bold green]")
        console.print("[dim]Using enhanced OpenRouter frontend API data[/dim]\n")
        
        try:
            groups = get_models_by_group()
            
            if not groups:
                console.print("[yellow]No model groups found.[/yellow]")
                Prompt.ask("Press Enter to continue")
                return select_model(config)
            
            # Sort groups by name and display
            sorted_groups = sorted(groups.keys())
            console.print("[bold magenta]Available Model Groups:[/bold magenta]")
            for i, group in enumerate(sorted_groups, 1):
                model_count = len(groups[group])
                console.print(f"[bold]{i}.[/bold] {group} [dim]({model_count} models)[/dim]")
            console.print("[bold]b[/bold] - Go back to main menu")
            
            group_choice = Prompt.ask("Select a group", default="1")
            
            if group_choice.lower() == 'b':
                return select_model(config)
            
            try:
                group_index = int(group_choice) - 1
                if 0 <= group_index < len(sorted_groups):
                    selected_group = sorted_groups[group_index]
                    group_models = groups[selected_group]
                    
                    console.print(f"[bold green]{selected_group} Models:[/bold green]")
                    console.print(f"[dim]Found {len(group_models)} models in this group[/dim]\n")
                    
                    for i, model in enumerate(group_models, 1):
                        # Skip None models in display
                        if model is None:
                            continue
                            
                        endpoint = model.get('endpoint', {}) if model else {}
                        model_name = model.get('slug') or model.get('name') or model.get('short_name', 'Unknown') if model else 'Unknown'
                        provider = endpoint.get('provider_name', 'Unknown') if endpoint else 'Unknown'
                        
                        # Show pricing info
                        pricing_info = ""
                        if endpoint and endpoint.get('is_free', False):
                            pricing_info = " [green](FREE)[/green]"
                        elif endpoint:
                            pricing = endpoint.get('pricing', {})
                            if pricing:
                                prompt_price = pricing.get('prompt', '0')
                                try:
                                    if float(prompt_price) > 0:
                                        pricing_info = f" [dim](${prompt_price}/token)[/dim]"
                                except:
                                    pass
                        
                        console.print(f"[bold]{i}.[/bold] {model_name} [dim]({provider})[/dim]{pricing_info}")
                    
                    console.print(f"\n[bold]b[/bold] - Go back to group selection")
                    
                    model_choice = Prompt.ask("Enter model number or 'b' to go back", default="1")
                    
                    if model_choice.lower() == 'b':
                        return select_model(config)
                    
                    try:
                        model_index = int(model_choice) - 1
                        if 0 <= model_index < len(group_models):
                            selected_model_obj = group_models[model_index]
                            if selected_model_obj:
                                selected_model = selected_model_obj.get('slug') or selected_model_obj.get('name') or selected_model_obj.get('short_name', 'Unknown')
                            else:
                                selected_model = 'Unknown'
                            console.print(f"[green]Selected {selected_model} from {selected_group} group[/green]")
                            
                            # Auto-detect thinking mode support
                            try:
                                auto_detect_thinking_mode(config, selected_model)
                            except Exception as e:
                                console.print(f"[yellow]Error detecting thinking mode: {str(e)}. Using default settings.[/yellow]")
                            return selected_model
                        else:
                            console.print("[red]Invalid selection[/red]")
                            Prompt.ask("Press Enter to continue")
                            return select_model(config)
                    except ValueError:
                        console.print("[red]Please enter a valid number[/red]")
                        Prompt.ask("Press Enter to continue")
                        return select_model(config)
                else:
                    console.print("[red]Invalid group selection[/red]")
                    return select_model(config)
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")
                return select_model(config)
                
        except Exception as e:
            console.print(f"[red]Error loading model groups: {str(e)}[/red]")
            console.print("[yellow]Falling back to standard model selection[/yellow]")
            Prompt.ask("Press Enter to continue")
            return select_model(config)