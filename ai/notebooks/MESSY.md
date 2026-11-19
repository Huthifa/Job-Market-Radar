# What's messy in the data

## Remotive
- The API ignores the `limit` parameter (asked for 5, got 17).
- The whole free feed is only ~17 jobs, so Hacker News became the main source.
- Usage rules: max 4 requests/day, link back and credit Remotive, jobs delayed 24h.
- Missing values hide as empty strings: `isna()` said salary was complete, but 5/17 were `""`.
- Salary is free text in 12 formats in 12 jobs: k/K, per hour, per month, per task, "OTE",
  no currency, European decimal comma ("$35,3k").
- The salary sits in a separate field, not in the description, so it was added to the description
  so the AI could see it.
- Descriptions are mostly HTML (inline styles, `<span>` tags): 1000 characters held ~150 of real text.
- About half the jobs aren't tech (Marketing, Customer Service, Writing, Sales).
- Dates have no time zone.

## Hacker News "Who is hiring?"
- One post per company, as free text: no fields at all.
- 89% (218/245) follow the "Company | Title | Location | ..." first-line pattern, but the ORDER
  varies, so the parsed "title" is often a city, "ONSITE", "Full-Time" or "All".
- Some posts hold several roles, each with its own skills and pay.
- Some posts aren't job ads: a single ".", a job seeker posting his own CV, a PhD position.
- HTML codes in the text (`&#x2F;` for "/", `&amp;` for "&").
- Dates are in UTC.

## Both
- The same skill appears under different names (Apache Airflow / airflow, K8s / kubernetes).
- Hourly and yearly pay can't be compared without a `salary_period` field.