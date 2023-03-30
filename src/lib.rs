use pyo3::prelude::*;
use rand::Rng;

const RATES: &'static [(f64, f64, f64)] = &[
    (0.95, 0.05, 0.0),
    (0.9, 0.1, 0.0),
    (0.85, 0.15, 0.0),
    (0.85, 0.15, 0.0),
    (0.8, 0.2, 0.0),
    (0.75, 0.25, 0.0),
    (0.7, 0.3, 0.0),
    (0.65, 0.35, 0.0),
    (0.6, 0.4, 0.0),
    (0.55, 0.45, 0.0),
    (0.5, 0.5, 0.0),
    (0.45, 0.55, 0.0),
    (0.4, 0.594, 0.006),
    (0.35, 0.637, 0.013),
    (0.3, 0.686, 0.014),
    (0.3, 0.679, 0.021),
    (0.3, 0.679, 0.021),
    (0.3, 0.679, 0.021),
    (0.3, 0.672, 0.028),
    (0.3, 0.672, 0.028),
    (0.3, 0.63, 0.07),
    (0.3, 0.63, 0.07),
    (0.03, 0.776, 0.194),
    (0.02, 0.686, 0.294),
    (0.01, 0.594, 0.396),
];

const INVALID: &'static [usize] = &[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20];

fn lvl0_9(lvl: usize, star: usize) -> i64 {
    let base: usize = (lvl.pow(3) * (star + 1) / 2500 + 10) / 1;
    100 * base as i64
}

fn lvl10_14(lvl: usize, star: usize) -> i64 {
    let base: f64 = (lvl as f64).powf(3.0) * ((star + 1) as f64).powf(2.7) / 40_000.0 + 10.0;
    100 * base as i64
}

fn lvl15_24(lvl: usize, star: usize) -> i64 {
    let base: f64 = (lvl as f64).powf(3.0) * ((star + 1) as f64).powf(2.7) / 20_000.0 + 10.0;
    100 * base as i64
}

fn get_costs(lvl: usize) -> Vec<i64> {
    let mut costs: Vec<i64> = vec![];
    for star in 0..25 {
        if star < 10 {
            costs.push(lvl0_9(lvl, star))
        } else if star < 15 {
            costs.push(lvl10_14(lvl, star))
        } else {
            costs.push(lvl15_24(lvl, star))
        }
    }
    costs
}

#[pyfunction]
fn starforce_single(start: usize, end: usize, lvl: usize) -> PyResult<(i64, i64, i64)> {
    let costs = get_costs(lvl);
    let mut current: usize = start as usize;
    let mut roll: f64;
    let mut tap_count: i64 = 0;
    let mut boom_count: i64 = 0;
    let mut cost: i64 = 0;
    let mut consecutive_fails: i8 = 0;
    let mut rng = rand::thread_rng();

    while current != end {
        let (succeed, fail, _boom) = RATES[current];
        tap_count += 1;

        cost += costs[current];
        roll = if consecutive_fails == 2 {
            0.0
        } else {
            rng.gen::<f64>()
        };

        // Success
        if roll <= succeed {
            current += 1;
            consecutive_fails += 1;
        }
        // Failure
        else if roll <= succeed + fail {
            if !INVALID.contains(&current) {
                current -= 1;
                consecutive_fails += 1;
            }
        }
        // Boom
        else {
            boom_count += 1;
            current = 12;
            consecutive_fails = 0;
        }
    }
    Ok((cost, tap_count, boom_count))
}

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn msds(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(starforce_single, m)?)?;
    Ok(())
}
