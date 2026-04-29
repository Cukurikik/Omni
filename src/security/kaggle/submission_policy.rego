package omni.security.kaggle

default allow_submission = false

allow_submission {
    input.user.rank >= "expert"
    input.submission.file_size_mb < 500
}

deny_leak {
    input.submission.contains_external_data == true
    input.competition.allow_external == false
}
