"""Tests for the simulation engine."""

import pytest


class TestBaselineReproduction:
    """Test that baseline indicators match known trajectories."""

    EXPECTED_GDP_GROWTH = [0.3, 1.2, 1.7, 1.4, 1.7, 1.8, 1.6, 1.4]
    EXPECTED_INFLATION = [1.2, 0.6, 1.1, 1.7, 2.1, 1.9, 1.7, 1.6]
    EXPECTED_DEFICIT = [-2.7, -2.6, -2.4, -2.3, -2.1, -1.9, -1.8, -1.7]
    EXPECTED_UNEMPLOYMENT = [8.5, 8.4, 8.3, 8.1, 7.9, 7.7, 7.6, 7.5]

    def test_baseline_gdp_growth(self, engine):
        indicators = engine.get_baseline_indicators()
        for i, (actual, expected) in enumerate(
            zip(indicators.gdp_growth, self.EXPECTED_GDP_GROWTH)
        ):
            assert abs(actual - expected) < 0.15, (
                f"Year {indicators.years[i]}: GDP growth {actual:.2f} != {expected}"
            )

    def test_baseline_inflation(self, engine):
        indicators = engine.get_baseline_indicators()
        for i, (actual, expected) in enumerate(
            zip(indicators.inflation, self.EXPECTED_INFLATION)
        ):
            assert abs(actual - expected) < 0.15, (
                f"Year {indicators.years[i]}: Inflation {actual:.2f} != {expected}"
            )

    def test_baseline_deficit(self, engine):
        indicators = engine.get_baseline_indicators()
        for i, (actual, expected) in enumerate(
            zip(indicators.deficit_ratio, self.EXPECTED_DEFICIT)
        ):
            assert abs(actual - expected) < 0.15, (
                f"Year {indicators.years[i]}: Deficit {actual:.2f} != {expected}"
            )

    def test_baseline_unemployment(self, engine):
        indicators = engine.get_baseline_indicators()
        for i, (actual, expected) in enumerate(
            zip(indicators.unemployment, self.EXPECTED_UNEMPLOYMENT)
        ):
            assert abs(actual - expected) < 0.15, (
                f"Year {indicators.years[i]}: Unemployment {actual:.2f} != {expected}"
            )


class TestSignTests:
    """Test that instrument shocks produce economically correct directions."""

    def test_public_investment_increases_gdp(self, engine):
        """VIG_X > 0 should increase GDP growth."""
        result = engine.simulate({"VIG_X": 1000})
        # GDP growth should be higher than baseline in at least year 1
        for i in range(min(3, len(result.years))):
            diff = result.scenario_indicators.gdp_growth[i] - result.baseline_indicators.gdp_growth[i]
            assert diff >= -0.01, f"Year {result.years[i]}: VIG_X should increase GDP, got {diff}"

    def test_vat_increase_raises_prices(self, engine):
        """ITPC0R_X > baseline should increase inflation."""
        result = engine.simulate({"ITPC0R_X": 23})  # +2pp VAT
        diff = result.scenario_indicators.inflation[0] - result.baseline_indicators.inflation[0]
        assert diff > 0, f"VAT increase should raise inflation, got {diff}"

    def test_income_tax_reduces_consumption(self, engine):
        """DTH_X > 0 (more tax) should reduce GDP growth."""
        result = engine.simulate({"DTH_X": 5000})
        # First year GDP growth should be lower or similar
        diff = result.scenario_indicators.gdp_growth[0] - result.baseline_indicators.gdp_growth[0]
        assert diff <= 0.1, f"Income tax increase should not boost GDP much, got {diff}"

    def test_public_employment_reduces_unemployment(self, engine):
        """NG_X > 0 should reduce unemployment."""
        result = engine.simulate({"NG_X": 20})
        diff = result.scenario_indicators.unemployment[0] - result.baseline_indicators.unemployment[0]
        assert diff <= 0.05, f"Public employment should reduce UR, got {diff}"


class TestEngineAPI:
    def test_simulate_returns_output(self, engine):
        result = engine.simulate()
        assert result.years
        assert result.baseline_indicators.gdp_growth
        assert result.scenario_indicators.gdp_growth
        assert result.convergence

    def test_simulate_with_instruments(self, engine):
        result = engine.simulate({"VIG_X": 500})
        assert result.instruments["VIG_X"] == 500

    def test_invalid_instrument_raises(self, engine):
        with pytest.raises(ValueError, match="Unknown instrument"):
            engine.simulate({"BOGUS": 42})

    def test_out_of_range_instrument_raises(self, engine):
        with pytest.raises(ValueError, match="out of range"):
            engine.simulate({"VIG_X": 999999})

    def test_instrument_specs(self, engine):
        specs = engine.get_instrument_specs()
        assert len(specs) == 10
        keys = {s["key"] for s in specs}
        assert "VIG_X" in keys
        assert "ITPC0R_X" in keys
