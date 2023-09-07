# Fit Score Algorithm

## Criteria (in order of importance)

### 1. State Licensure with all states that have reciprocity

#### Notes

- Nurse Licensure Compact (NLC or eNLC) allows nurses to hold one multi-state license and practice in the nurse's home state or any of the other 40 states in the NLC.
	+ [eNLC States](https://nurse.org/articles/enhanced-compact-multi-state-license-enlc/)
- If a nurse has worked in once of these 40 states, I believe that means they have an eNLC
- We should probably make a column in the `NURSE` table like `HASENLC`
#### Scoring System

- 1 if current license **can** be applied to state of facility
- 0 if current license **cannot** be applied to state of facility

### 2. Specialty and Discipline

#### Criteria

While they are all RNs, but are they ICU, ER, L&D and so on 

#### Scoring System
- Number of hours worked under each specialty/discipline

- 1 if nurse **has** history being the specialty that is requested
- 0 if nurse **does not** have history being the specialty that is requested


### 3. Credentialed based on recency of having worked with the nurse staffing firm

#### Criteria

- Current
- Within last year

#### Scoring System

- 1 if currently employed through a TRS-arranged contract **and** the end date of contract is before the requisition's expected start date
- 0.9 if a TRS-arranged contract ended in last 6 months
- 0.75 if a TRS-arranged contract ended in the last year
- 0.5 if nurse has ever had a contract through TRS
- 0 if nurse has never had a contract through TRS

### 4. End date of current assignment

#### Criteria

Within 5 weeks of current 13-week assignment ending 


#### Notes

- Ensure the current contract's end date is before the new contract's expected start date

#### Scoring System
- 1 if nurse is available now or nurse's current contract will end before the requisition's expected start date
- 0.40 if nurse's contract is within 1 week of ending
- 0.25 if nurse's contract is within 5 weeks of ending
- 0.10 if nurse's contract is within 10 weeks of ending
- 0 if nurse's contract is more than 10 weeks of ending


### 5. Years of Experience

#### Criteria

- Target HCPs with 3+ YoE

#### Scoring System

- If YoE not specified
	+ YoE/10
- If YoE specified
	+ YoE/10
	+ filter out anyone with too few YoE for requisition

### 6. Proximity to location
#### Scoring System
##### Easier Approach
- 1 if same state **and** same city
- 0.50 if same state **but** not same city
- 0 if not same state

##### Complex Approach
- 5 miles: 1
- 10 miles: 0.9
- 15 miles: 0.8
- 25 miles: 0.7
- 50 miles: 0.6
- 100 miles: 0.5
- 500 miles: 0.4
- 1000+ miles: 0.0

Anything like ~25 miles or more   
Depends on if the facility is in a city or not (due to traffic)


## Approach Options
- Local development using Pandas
	+ On-the-fly calculations
- Pure Snowpark
	+ On-the-fly calculations
- SQL
	+ `MATCHING` table:
		* `NEEDID`
		* `NURSEID`
		* `LICENSURESCORE`
		* `SPECIALITYSCORE`
		* `CREDENTIALEDSCORE`
		* `AVAILABLITYSCORE`
		* `YEARSOFEXPERIENCESCORE`
		* `PROXIMITYSCORE`
	+ Procedure that takes in `NEEDID` and all the nurses and writes results to `MATCHING`


## Terminology

- [NCLEX: National Council Licensure Examination](https://en.wikipedia.org/wiki/National_Council_Licensure_Examination)

### [Types of Associate Degree in Nursing](https://nurse.org/education/adn-guide/)
#### Degrees
- ADN: Associate's Degree in Nursing (2-year program)
- ASN: Associate of Science Degree in Nursing
- AAS: Associate of Applied Science in Nursing
#### Jobs
- Family medicine
- Pediatrics
- Emergency
- Oncology
- Surgery
- Radiology

- BSN: Bachelor's of Science in Nursing (4-year program)



## Miscellaneous Notes
- CNAs work along side RNs and thus can't do jobs that RNs can
- LPNs (LPN-LVN) don't require as much school as RNs and thus can't do the same jobs as RNs