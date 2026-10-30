# Research retrospective

The deliberately injected optimizer override was detectable only through live SGD observation, despite an unchanged spec. Add that hook after trainer overrides in future integrations. The metric injection was caught by recomputing from prediction artifacts and actual labels. These findings justify mechanical guards, not an assumption that arbitrary telemetry is trustworthy. Budget/seed controls and real domain data are the next methodological limits. Keep local evidence as the source of continuity when a tracker is unavailable.
