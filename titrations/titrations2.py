# AUTOGENERATED! DO NOT EDIT! File to edit: ../titrations2.ipynb.

# %% auto 0
__all__ = ['htn_target', 'DosingLadder', 'Rule', 'ConditionalRule', 'Action', 'Start', 'DoNotStart', 'StepUp', 'StepDown',
           'Continue', 'Stop', 'MarkMaxDose', 'ReportReaction', 'RuleWithActions', 'ConditionalRuleWithActions',
           'ClassLimitingRule', 'TitrationLimitingRule', 'NonLimitingRule', 'ConditionTitrationLimitingRule',
           'MaxTolerated', 'Titrator']

# %% ../titrations2.ipynb 1
from typing import List, Dict, Any, Optional
from .basics import *

# %% ../titrations2.ipynb 5
class DosingLadder:
    ladder : Dict[str, List[Medication]]

    def __init__(self, ladder_dict : Dict[str, List[Medication]], single_class : bool = True) -> None:
        # TODO: ensure 'subladders' have the same number of steps

        # TODO: ensure each subladder consists of the same ingredient

        if single_class:
            pass # TODO: ensure all medications are of the same class

        self.ladder = ladder_dict
        # self.ingredient = None
        self.med_class = None

    @property
    def ingredients(self) -> List[Ingredient]:
        # TODO this should be okay if the checks in `__init__` are implemented
        return [self.ladder[med_name][0].ingredient for med_name in self.ladder]

    def get_subladder(self, medication : Ingredient | Medication):
        return self.ladder[medication.name]

    def _get_current_step_index(self, current_med : Medication):
        subladder = self.get_subladder(current_med)
        index = next((i for i, med in enumerate(subladder) if med.dose == current_med.dose), None)
        return index
    
    def _is_at_lowest_step(self, current_med : Medication):
        return current_med.dose == self.get_lowest_step(current_med).dose

    def _is_at_highest_step(self, current_med : Medication):
        return current_med.dose == self.get_highest_step(current_med).dose
    
    def get_next_step_up(self, current_med : Medication):
        current_dose_index = self._get_current_step_index(current_med)
        return self.get_subladder(current_med)[current_dose_index + 1]

    def get_next_step_down(self, current_med : Medication):
        current_dose_index = self._get_current_step_index(current_med)
        return self.get_subladder(current_med)[current_dose_index - 1]
    
    def get_lowest_step(self, medication: Ingredient | Medication):
        return self.get_subladder(medication)[0]

    def get_highest_step(self, medication: Ingredient | Medication):
        return self.get_subladder(medication)[-1]
    
    def get_current_medication_for_patient(self, patient : Patient):
        filtered = list(filter(lambda med: med.ingredient in self.ingredients, patient.medications))
        assert len(filtered) <= 1
        return filtered[0] if filtered else None
    
    @property
    def lowest_steps(self):
        return { med_name : self.ladder[med_name][0] for med_name in self.ladder}
    
    @property
    def highest_steps(self):
        return { med_name : self.ladder[med_name][-1] for med_name in self.ladder}

# %% ../titrations2.ipynb 20
import operator

class Rule:
    parameter : str
    operation : str
    threshold : Any

    operators = {
        "gt": operator.gt,
        "gte": operator.ge,
        "lt": operator.lt,
        "lte": operator.le,
        "eq": operator.eq,
        "neq": operator.ne,
        "in": operator.contains,
    }

    def __init__(self, parameter:str, operation:str, threshold:Any) -> None:
        # assert parameter in VALID_PARAMETERS, "Not a valid parameter"
        assert operation in self.operators, f"Invalid operator {operation}"
        if operation == "in": print(f"Warning: For 'in' operations, it is recommended to use kwargs explicitly.")

        self.parameter = parameter
        self.operation = operation
        self.threshold = threshold

    def _is_satisfied(self, patient : Patient):
        # FIXME: handle 'in' operation more neatly

        patient_value = getattr(patient, self.parameter, None)  
        if patient_value is None:  # FIXME: this should be reviewed again
            if type(self.threshold) == bool: raise ValueError(f"Patient has no attribute `{self.parameter}`.")
            else: return False

        # if self.operation == "in": return self.operators[self.operation](self.threshold, patient_value)
        # else:
        return self.operators[self.operation](patient_value, self.threshold)

    def _get_eval_result_object(self, is_satisfied : bool, patient : Optional[Patient] = None) -> Any:
        return type('RuleEvalResult', (), {
            'rule': self,
            'is_satisfied': is_satisfied,
        })

    def evaluate(self, patient : Patient):
        is_satisfied = self._is_satisfied(patient)
        return self._get_eval_result_object(is_satisfied, patient)
    
    def __repr__(self) -> str:
        return f"{self.parameter} {self.operation} {self.threshold}"

# %% ../titrations2.ipynb 24
class ConditionalRule(Rule):
    condition : Rule

    def __init__(self, parameter:str, operation:str, threshold:Any, condition:Rule) -> None:
        super().__init__(parameter, operation, threshold)
        self.condition = condition

    def _condition_is_met(self, patient: Patient):
        return self.condition.evaluate(patient).is_satisfied

    def _is_satisfied(self, patient: Patient, condition_is_met: bool):
        return super()._is_satisfied(patient) if condition_is_met else False

    def evaluate(self, patient: Patient):
        condition_is_met = self._condition_is_met(patient)
        is_satisfied = self._is_satisfied(patient, condition_is_met)
        return self._get_eval_result_object(is_satisfied, patient)


# %% ../titrations2.ipynb 29
class Action:
    """
    This is a base class for 'Action' classes to build upon.
    """
    def __init__(self,
                 patient : Patient,
                 dosing_ladder : DosingLadder,
                 current_medication : Medication):
        self.patient = patient
        self.dosing_ladder = dosing_ladder
        self.current_medication = current_medication

    def suggest(self):
        pass

    def buttons(self):
        pass

    def perform(self):
        pass

# %% ../titrations2.ipynb 30
class Start(Action):
    """
    Start a new medication.
    """
    def __init__(self, patient: Patient, dosing_ladder: DosingLadder, current_medication: Medication):
        super().__init__(patient, dosing_ladder, current_medication)
        self.lowest_steps = self.dosing_ladder.lowest_steps

    def suggest(self):
        med_names = list(self.lowest_steps)
        # TODO: this should only be done if the ladder has 3+ subladders
        return f"Start {', '.join([str(self.lowest_steps[med]) for med in med_names[:-1]])}, or {str(self.lowest_steps[med_names[-1]])}."

    def buttons(self):
        return [str(self.lowest_steps[med]) for med in self.lowest_steps]

    def perform(self):
        # TODO: implement this
        pass

# %% ../titrations2.ipynb 33
class DoNotStart(Action):
    """
    Do not start a new medication.
    """
    def suggest(self):
        # TODO: modify to suggest not starting a class
        pass

    def perform(self):
        pass

# %% ../titrations2.ipynb 34
class StepUp(Action):
    """
    Step up one dose on the dosing ladder.
    """
    def suggest(self):
        next_step_up = self.dosing_ladder.get_next_step_up(self.current_medication)
        return f"Increase {self.current_medication.name} to {str(next_step_up)}."

    def perform(self):
        pass

# %% ../titrations2.ipynb 35
class StepDown(Action):
    """
    Step down one dose on the dosing ladder.
    """
    def suggest(self):
        next_step_down = self.dosing_ladder.get_next_step_down(self.current_medication)
        return f"Decrease {self.current_medication.name} to {str(next_step_down)}."

    def perform(self):
        pass

# %% ../titrations2.ipynb 36
class Continue(Action):
    """
    Continue the medication at the same dose.
    """
    def suggest(self):
        return f"Continue {str(self.current_medication)}."

    def perform(self):
        pass

# %% ../titrations2.ipynb 37
class Stop(Action):
    """
    Stop the medication.
    """
    def suggest(self):
        return f"Stop {self.current_medication.name}."

    def perform(self):
        pass

# %% ../titrations2.ipynb 38
class MarkMaxDose(Action):
    """
    Mark current dose as maxiumum tolerated dose.
    """
    def suggest(self):
        return f"Mark {str(self.current_medication)} as maximum tolerated dose."
    
    def perform(self):
        pass

# %% ../titrations2.ipynb 39
class ReportReaction(Action):
    """
    File an adverse reaction record.
    """
    def suggest(self):
        return f"File an adverse reaction to {self.current_medication.name}"

    def perform(self, description="reaction"):
        # In real life, this could be opening a modal for entering adverse reactions instead
        self.patient.reactions.append(
            Reaction(self.current_medication.ingredient, description),
        )

# %% ../titrations2.ipynb 41
class RuleWithActions(Rule):
    actions_when_satisfied : List[Action] = []
    actions_when_not_satisfied : List[Action] = []
    default_actions_when_satisfied : List[Action] = []  # class attribute
    default_actions_when_not_satisfied : List[Action] = []  # class attribute
    
    def __init__(self,
                 parameter: str, operation: str, threshold: Any,
                 additional_actions_when_satisfied: List[Action] = [],
                 additional_actions_when_not_satisfied: List[Action] = []) -> None:
        super().__init__(parameter, operation, threshold)
        self.actions_when_satisfied = self.default_actions_when_satisfied + additional_actions_when_satisfied
        self.actions_when_not_satisfied = self.default_actions_when_not_satisfied + additional_actions_when_not_satisfied

    def _get_eval_result_object(self, is_satisfied: bool, patient: Patient) -> Any:
        result = super()._get_eval_result_object(is_satisfied, patient)

        recommended_actions = self.actions_when_satisfied if is_satisfied \
            else self.actions_when_not_satisfied
        
        # Recursively evaluate actions that are rules
        for action in recommended_actions:
            if isinstance(action, RuleWithActions):
                action_result = action.evaluate(patient)
                recommended_actions.remove(action)
                recommended_actions += action_result.recommended_actions

        result.recommended_actions = recommended_actions
        return result

class ConditionalRuleWithActions(ConditionalRule, RuleWithActions):
    pass

# %% ../titrations2.ipynb 42
class ClassLimitingRule(RuleWithActions):
    default_actions_when_satisfied = [Stop, ReportReaction]

class TitrationLimitingRule(RuleWithActions):
    default_actions_when_satisfied = [Continue, StepDown, MarkMaxDose]

class NonLimitingRule(RuleWithActions):
    pass

# %% ../titrations2.ipynb 43
class ConditionTitrationLimitingRule(ConditionalRule, TitrationLimitingRule):
    def _get_eval_result_object(self, is_satisfied: bool, patient: Patient) -> Any:
        # TODO: this is not a neat solution, will need to think of a better way
        return TitrationLimitingRule._get_eval_result_object(self, is_satisfied, patient)

# %% ../titrations2.ipynb 49
class MaxTolerated(RuleWithActions):
    actions_when_satisfied = [Continue]
    def __init__(self, dosing_ladder : DosingLadder, current_medication : Optional[Medication] = None) -> None:
        self.dosing_ladder = dosing_ladder
        self.current_medication = current_medication

    def _is_satisfied(self, patient: Patient):
        if not self.current_medication: self.current_medication = self.dosing_ladder.get_current_medication_for_patient(patient)
        if self.current_medication and self.current_medication.name in patient.max_tolerated:
            return str(self.current_medication) == str(patient.max_tolerated[self.current_medication.name])
        return False
    
    def __repr__(self) -> str:
        return "Max tolerated dose?"

# %% ../titrations2.ipynb 51
htn_target = RuleWithActions('SBP', 'lt', 130, additional_actions_when_satisfied=[Continue])

# %% ../titrations2.ipynb 53
from inspect import isclass
from itertools import chain

class Titrator:
    patient : Patient
    dosing_ladder : DosingLadder

    current_medication : Medication
    
    # class attributes
    default_titration_target : type[Rule] | Rule
    default_rules : List[RuleWithActions]
    default_initiation_rules : List[RuleWithActions]
    default_titration_rules : List[RuleWithActions]
    default_initiation_actions : List[Action] = [Start]
    default_titration_actions : List[Action] = [StepUp]
    
    # instance attributes
    titration_target : Rule
    rules : List[RuleWithActions]
    initiation_rules : List[RuleWithActions]
    titration_rules : List[RuleWithActions]
    initiation_actions : List[Action]
    titration_actions : List[Action]

    can_advance : bool
    satisfied_rules : List[Rule]
    recommended_actions : List[Action]

    def __init__(self, patient : Patient,
                 dosing_ladder : Optional[DosingLadder] = None,
                 titration_target : type[Rule] | Rule = MaxTolerated) -> None:
        self.patient = patient

        if dosing_ladder: self.dosing_ladder = dosing_ladder
        else: assert hasattr(self, 'dosing_ladder'), "Dosing ladder must be specified."

        self.current_medication = self.dosing_ladder.get_current_medication_for_patient(patient)

        if isclass(titration_target):
            self.titration_target = titration_target(self.dosing_ladder, self.current_medication)
        else:
            self.titration_target = titration_target

        # TODO: assert hasattr(self, 'titration_target')
        # assert hasattr(self, 'default_rules') or (hasattr(self, 'default_initiation_rules') and \
        #        hasattr(self, 'default_titration_rules')), "Rules must be specified."
        
        self.rules = self.default_rules + [self.titration_target]

        self.initiation_actions = self.default_initiation_actions  # TODO: allow override
        self.titration_actions = self.default_titration_actions  # TODO: allow override

    @property
    def current_ingredient(self) -> Ingredient:
        return self.current_medication.ingredient if self.current_medication else None

    @property
    def is_initiating(self) -> bool:
        return self.current_medication == None

    @property
    def is_titrating(self) -> bool:
        return not self.is_initiating
    
    def evaluate(self) -> None:
        self._rule_results = map(lambda rule: rule.evaluate(self.patient), self.rules)
        self._results_satisfied = list(filter(lambda result: result.is_satisfied, self._rule_results))
        self.satisfied_rules = list(map(lambda result: result.rule, self._results_satisfied))
        
        self.can_advance = len(self.satisfied_rules) == 0

        if self.can_advance:
            if self. is_initiating:
                self.recommended_actions = [action(self.patient, self.dosing_ladder, self.current_medication) for action in self.initiation_actions]
            else:
                self.recommended_actions = [action(self.patient, self.dosing_ladder, self.current_medication) for action in self.titration_actions]
        else:
            action_lists = [result.recommended_actions for result in self._results_satisfied]
            self.recommended_actions = [action(
                self.patient, self.dosing_ladder, self.current_medication
                ) for action in set(chain.from_iterable(action_lists))]


