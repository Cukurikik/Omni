fn main() {
    let s = std::fs::read_to_string("../Omnifile.toml").unwrap();
    match s.parse::<toml::Table>() {
        Ok(_) => println!("TOML Table API Works!"),
        Err(e) => println!("ERROR Table: {:?}", e)
    }
}
