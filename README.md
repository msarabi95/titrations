# MedTitrator

An open-source, generalized clinical decision support tool for medication titration.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/msarabi95/titrations/HEAD)

## Overview

MedTitrator is a Python-based framework that provides comprehensive support for medication titration algorithms in clinical decision support (CDS) systems. Medication titration is a central aspect of many clinical guidelines, but supporting titration in CDS systems is challenging due to multiple complexities such as:

- Condition-specific and patient-specific maximum tolerated doses (e.g., based on age or renal clearance)
- The need to account for physiological response
- The need to switch agents within a drug class due to issues such as changing insurance formulary coverage

Existing algorithms and tools address these issues partially, but MedTitrator provides the first comprehensive solution for managing medication titration in clinical decision support tools.

## Key Features

### Generic Object-Oriented Data Model

MedTitrator is built on a generic, object-oriented data model for representing medication titration knowledge. The core components include:

- **Titrator**: A data structure that represents a complete medication titration algorithm
- **Titration Target**: A conditional statement about a particular attribute of a patient (e.g., "maximum tolerated dose")
- **Rules**: Conditional statements that suggest certain actions depending on whether specific criteria are met
- **Dosing Ladder**: An ordered listing of stepwise increments of a particular medication or group of medications
- **Actions**: Recommendations that could be made by the titration algorithm (e.g., start, stop, step up, step down)

### Pre-defined Actions

MedTitrator comes with several reusable actions:

- `Start` - Start a new medication
- `Stop` - Stop a medication
- `StepUp` - Increase medication dose
- `StepDown` - Decrease medication dose
- `Continue` - Continue current medication
- `MarkMaxDose` - Mark current dose as maximum tolerated
- `DoNotStart` - Do not start a medication
- `ReportReaction` - Report an adverse reaction

### Specialized Rule Types

Common patterns are abstracted into distinct rule subsets:

- **TitrationLimitingRule**: Rules that suggest decreasing the current medication dose by 1 step but do not completely preclude the use of that medication
- **ClassLimitingRule**: Rules that result in stopping the medication class
- **ConditionalRule**: Rules that are triggered only in the presence of a certain condition

## Validation: HFrEF GDMT Use Case

MedTitrator was evaluated for its capacity to support actual clinical guidelines by implementing titration of 4 medication classes according to the 2022 AHA/ACC/HFSA Heart Failure with Reduced Ejection Fraction (HFrEF) guidelines:

1. **Beta Blockers** (carvedilol, metoprolol succinate, bisoprolol)
2. **Renin-Angiotensin-Aldosterone System (RAAS) Inhibitors**
3. **Sodium-Glucose Co-Transporter 2 (SGLT2) Inhibitors**
4. **Mineralocorticoid Receptor Antagonists**

For each medication class, MedTitrator was configured with:
- A dosing ladder containing incremental doses
- A titration target of "maximum tolerated"
- Titration-limiting rules including hypotension, bradycardia, high-grade atrioventricular block, and clinical symptoms

MedTitrator successfully captured all the conditional logic necessary for these use cases and produced recommendations matching those made by a licensed clinician for various sets of patient parameters.

## Repository Structure

```
titrations/
├── basics.ipynb          # Basic data structures (Patient, Medication, Ingredient, etc.)
├── titrations.ipynb      # Core titration framework components
├── titrations2.ipynb     # Advanced titration features and rules
├── demo.ipynb            # Comprehensive demo and usage examples
├── examples.ipynb        # Real-world examples
├── titrations/           # Python module directory
├── LICENSE               # MIT License
└── README.md            # This file
```

## Getting Started

### Installation

Clone the repository:

```bash
git clone https://github.com/msarabi95/titrations.git
cd titrations
```

### Basic Usage

The framework consists of three main modules:

1. **basics** - EHR-like functionalities including:
   - `Patient` - Patient data and medications
   - `Medication` - Medication information and dosing
   - `Ingredient` - Medication ingredients and classes
   - `Reaction` - Adverse reactions and allergies

2. **titrations** - Core titration framework elements:
   - `Rule` - Conditional statements for patient parameters
   - `DosingLadder` - Ordered medication doses
   - `Action` - Recommended actions (Start, Stop, StepUp, StepDown, etc.)
   - `Titrator` - Main algorithm that combines all components

3. **examples** - Pre-configured examples for common use cases

### Example: Beta Blocker Titration for HFrEF

```python
from titrations.basics import *
from titrations.titrations2 import *
from titrations.examples import *

# Create a patient
patient = Patient(SBP=110, HR=70, medications=[], has_pacemaker=False, 
                  decompensated=False, av_block=False, symptomatic=False)

# Create a titrator instance
titrator = BetaBlockerHFrEFTitrator(patient)

# Evaluate the patient
titrator.evaluate()

# Check if advancement is recommended
if titrator.can_advance:
    print("Recommended actions:", titrator.recommended_actions)
    print("Recommendation:", titrator.recommended_actions[0].suggest())
else:
    print("Cannot advance - limiting factors:", titrator.satisfied_rules)
```

### Notebooks

For comprehensive examples and demonstrations:

- **demo.ipynb** - Full walkthrough of all framework components with practical examples
- **examples.ipynb** - Additional real-world use cases
- **basics.ipynb** - Basic data structures and EHR-like functionalities

## Supported Patient Parameters

The framework supports the following patient parameters:

- `SBP` - Systolic Blood Pressure
- `HR` - Heart Rate
- `K` - Potassium level
- `Cr` - Creatinine
- `eGFR` - Estimated Glomerular Filtration Rate
- `decompensated` - Heart failure decompensation status
- `symptomatic` - Symptom status
- `has_pacemaker` - Pacemaker presence
- `av_block` - Atrioventricular block status
- `severe_gu_infxns` - Severe genitourinary infections
- `has_type_1_diabetes` - Type 1 diabetes
- `has_type_2_diabetes_on_insulin` - Type 2 diabetes on insulin

## Authors

**Saeed Arabi, MBBS¹**
**Kensaku Kawamoto, MD, PhD, MHS, FACMI, FAMIA¹**

¹ University of Utah, Salt Lake City, Utah

This work was partially supported by the Margolis Foundation.

## License

MedTitrator is released under the MIT License. See [LICENSE](LICENSE) for details.

## Citation

If you use MedTitrator in your research or clinical system, please cite:

Arabi, S., & Kawamoto, K. (2024). MedTitrator: An Open-Source, Generalized Clinical Decision Support Tool for Medication Titration. University of Utah.

## References

1. Kuperman G, Bobb A, Payne T, et al. Medication-related Clinical Decision Support in Computerized Provider Order Entry Systems: A Review. *JAMIA*. 2007;14(1):29-40.

2. Heidenreich PA, Bozkurt B, Aguilar D, et al. 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure. *Circulation*. 2022;145:e895-e1032.

## Future Directions

Further validation will be needed to verify MedTitrator's generalizability to other medical conditions beyond HFrEF. The framework is designed to be extensible and can be adapted to support titration algorithms for various therapeutic domains.

## Support

For questions, issues, or suggestions, please visit the [GitHub repository](https://github.com/msarabi95/titrations/).
