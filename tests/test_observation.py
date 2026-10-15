from landmarks import upright_points

from holdup.observation import NoPerson, UserSeen, observation_from


def test_with_several_people_in_frame_the_largest_one_is_the_user():
    user = upright_points(scale=1.0)
    passer_by = upright_points(scale=0.4)

    assert observation_from([passer_by, user]) == UserSeen(user)


def test_with_nobody_in_frame_there_is_no_person():
    assert observation_from([]) == NoPerson()
