from bw.commands.modals.mission_making import human_upload_error, upload_error_allows_force


def test__human_upload_error__uses_server_body_when_no_known_pattern_matches():
    assert human_upload_error('very strange backend failure') == 'Message from server: very strange backend failure'


def test__human_upload_error__turns_known_backend_error_into_member_friendly_text():
    assert human_upload_error('mission needs to be binarized to upload') == (
        'Missions need to be binarized to be uploaded to the server'
    )


def test__upload_error_allows_force__only_for_expected_validation_errors():
    assert upload_error_allows_force('not saved with POTATO') is True
    assert upload_error_allows_force('User does not have enough permissions to access this resource') is False
