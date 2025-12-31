import pytest

from ..harmony_domain import Note, NoteName
from ..enharmonic_resolver import CircleIndexCalculator


class TestCircleIndexCalculator:
    @pytest.fixture(autouse=True)
    def before_each_test(self):
        self.patient = CircleIndexCalculator()

    @staticmethod
    def will_calculate_circle_index_closest_to_tonal_center_data():
        params = []

        circle_index_a = 3  # tonal center
        wrapped_pitch_g_sharp = 11  # input wrapped pitch
        g_sharp_circle_index = 8  # expected that G# is closer to A than Ab
        params.append(
            pytest.param(circle_index_a, wrapped_pitch_g_sharp, g_sharp_circle_index)
        )

        circle_index_c = 0  # tonal center
        wrapped_pitch_d_flat = 4  # input wrapped pitch
        d_flat_circle_index = -5  # expected that Db is closer to C than C#
        params.append(
            pytest.param(circle_index_c, wrapped_pitch_d_flat, d_flat_circle_index)
        )

        circle_index_g = 1  # tonal center
        wrapped_pitch_d = 5  # input wrapped pitch
        d_natural_circle_index = (
            2  # expected that D is closer to G than F## or Abb or anything crazy
        )
        params.append(
            pytest.param(circle_index_g, wrapped_pitch_d, d_natural_circle_index)
        )

        circle_index_e_flat = -3  # tonal center
        wrapped_pitch_f_flat = 7  # input wrapped pitch
        f_flat_circle_index = -8  # expected that Fb is closer to Eb than E natural
        params.append(
            pytest.param(circle_index_e_flat, wrapped_pitch_f_flat, f_flat_circle_index)
        )

        return params

    @pytest.mark.parametrize(
        "tonal_center_circle_index, wrapped_pitch, expected_circle_index",
        will_calculate_circle_index_closest_to_tonal_center_data(),
    )
    def test_will_calculate_circle_index_closest_to_tonal_center(
        self,
        tonal_center_circle_index: int,
        wrapped_pitch: int,
        expected_circle_index: int,
    ):
        actual_circle_index = (
            self.patient.circle_index_for_enharmonic_equivalent_closest_to_tonal_center(
                wrapped_pitch=wrapped_pitch,
                tonal_center_circle_index=tonal_center_circle_index,
            )
        )

        assert actual_circle_index == expected_circle_index

    def test_will_return_none_for_pitch_outside_scale(self):
        tonal_center_circle_index = 0  # C
        pitch_outside_scale = 1  # A#/Bb

        assert not self.patient.circle_index_for_enharmonic_equivalent_within_scale_if_exists(
            wrapped_pitch=pitch_outside_scale,
            scale_tonal_center_circle_index=tonal_center_circle_index,
        )

    @staticmethod
    def will_apply_correct_key_signature_in_e_major_data():
        params = []

        pitch_e = 7
        circle_index_e = 4
        params.append(pytest.param(pitch_e, circle_index_e))
        pitch_f_sharp = 9
        circle_index_f_sharp = 6
        params.append(pytest.param(pitch_f_sharp, circle_index_f_sharp))
        pitch_g_sharp = 11
        circle_index_g_sharp = 8
        params.append(pytest.param(pitch_g_sharp, circle_index_g_sharp))
        pitch_a = 0
        circle_index_a = 3
        params.append(pytest.param(pitch_a, circle_index_a))
        pitch_b = 2
        circle_index_b = 5
        params.append(pytest.param(pitch_b, circle_index_b))
        pitch_c_sharp = 4
        circle_index_c_sharp = 7
        params.append(pytest.param(pitch_c_sharp, circle_index_c_sharp))
        pitch_d_sharp = 6
        circle_index_d_sharp = 9
        params.append(pytest.param(pitch_d_sharp, circle_index_d_sharp))

        return params

    @pytest.mark.parametrize(
        "wrapped_pitch, expected_circle_index",
        will_apply_correct_key_signature_in_e_major_data(),
    )
    def test_will_apply_correct_key_signature_in_e_major(
        self, wrapped_pitch: int, expected_circle_index: int
    ):
        tonal_center_circle_index = 4  # E

        predicted_circle_index = (
            self.patient.circle_index_for_enharmonic_equivalent_within_scale_if_exists(
                wrapped_pitch=wrapped_pitch,
                scale_tonal_center_circle_index=tonal_center_circle_index,
            )
        )

        assert predicted_circle_index == expected_circle_index

    @staticmethod
    def will_convert_from_circle_index_to_note_data():
        return [
            pytest.param(0, Note(NoteName.C, 0)),
            pytest.param(6, Note(NoteName.F, 1)),
            pytest.param(12, Note(NoteName.B, 1)),
            pytest.param(13, Note(NoteName.F, 2)),
            pytest.param(-1, Note(NoteName.F, 0)),
            pytest.param(-7, Note(NoteName.C, -1)),
            pytest.param(-9, Note(NoteName.B, -2)),
        ]

    @pytest.mark.parametrize(
        "circle_index, expected_note", will_convert_from_circle_index_to_note_data()
    )
    def test_will_convert_from_circle_index_to_note(
        self, circle_index: int, expected_note: Note
    ):
        converted_note = self.patient.convert_circle_index_to_note(circle_index)

        assert converted_note == expected_note
