use pyo3::prelude::*;
mod starforce_functions;

/// A python datascience toolkit for MapleStory
#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(starforce_functions::_starforce, m)?)?;
    m.add_function(wrap_pyfunction!(starforce_functions::_starforce_mt, m)?)?;
    m.add_function(wrap_pyfunction!(starforce_functions::_starforce_single, m)?)?;
    m.add_function(wrap_pyfunction!(
        starforce_functions::_starforce_benchmark,
        m
    )?)?;
    Ok(())
}
