use kdam::tqdm;
use pyo3::prelude::*;
use rand::Rng;
use std::thread;

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
pub fn _starforce_single(start: usize, end: usize, lvl: usize) -> PyResult<(i64, i64, i64)> {
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

fn starforce_single_rust(start: usize, end: usize, costs: &Vec<i64>) -> (i64, i64, i64) {
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
    (cost, tap_count, boom_count)
}

#[pyfunction]
pub fn _starforce(
    start: usize,
    end: usize,
    lvl: usize,
    n: usize,
    progress: bool,
) -> PyResult<Vec<(i64, i64, i64)>> {
    let costs = get_costs(lvl);
    let result: Vec<(i64, i64, i64)> = tqdm!(0..n, total = n, disable = !progress)
        .map(|_| -> (i64, i64, i64) { starforce_single_rust(start, end, &costs) })
        .collect();
    Ok(result)
}

fn _starforce_mt_single(
    start: usize,
    end: usize,
    lvl: usize,
    n: usize,
    progress: bool,
    position: u16,
) -> PyResult<Vec<(i64, i64, i64)>> {
    let costs = get_costs(lvl);
    let result: Vec<(i64, i64, i64)> =
        tqdm!(0..n, total = n, disable = !progress, position = position)
            .map(|_| -> (i64, i64, i64) { starforce_single_rust(start, end, &costs) })
            .collect();
    Ok(result)
}

#[pyfunction]
pub fn _starforce_mt(
    start: usize,
    end: usize,
    lvl: usize,
    n: usize,
    progress: bool,
) -> PyResult<Vec<(i64, i64, i64)>> {
    let cores: usize = thread::available_parallelism()?.get();
    let mut handles = vec![];
    let mut results: Vec<(i64, i64, i64)> = vec![];
    let div = n / cores;
    let n_mod = n % cores;
    let mut ns: Vec<usize> = (0..cores).map(|_| div).collect();
    if n_mod > 0 {
        for i in 0..n_mod {
            ns[i] += 1;
        }
    }
    for i in 0..cores {
        let subn = ns[i].clone();
        let handle = thread::spawn(move || {
            _starforce_mt_single(
                start.clone(),
                end.clone(),
                lvl.clone(),
                subn,
                progress.clone(),
                i as u16,
            )
        });
        handles.push(handle)
    }
    for handle in handles {
        let mut result = handle.join().unwrap().unwrap();
        results.append(&mut result);
    }
    if progress {
        println!("{}", String::from("\n").repeat(cores - 1))
    }
    Ok(results)
}

#[pyfunction]
pub fn _starforce_benchmark(start: usize, end: usize, lvl: usize, n: usize) -> PyResult<()> {
    let costs = get_costs(lvl);
    for _ in 0..n {
        starforce_single_rust(start, end, &costs);
    }
    Ok(())
}
