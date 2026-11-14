//! hello_gui — one binary, two faces.
//!
//!   GUI (default):  ./hello_gui
//!   CLI:            ./hello_gui cli "more text"
//!                   ./hello_gui cli -m "more text"
//!
//! Both paths use the SAME greeting logic from the `core` module below.

use clap::{Parser, Subcommand};
use eframe::egui;

// ---------------------------------------------------------------------------
// Core: the shared logic. No UI code here — CLI and GUI both call this.
// ---------------------------------------------------------------------------
mod core {
    /// The one function both front-ends share.
    /// `extra` is optional additional text appended to the greeting.
    pub fn greeting(extra: Option<&str>) -> String {
        match extra.map(str::trim).filter(|s| !s.is_empty()) {
            Some(text) => format!("Hello, world! {text}"),
            None => "Hello, world!".to_string(),
        }
    }
}

// ---------------------------------------------------------------------------
// CLI: argument parsing with clap.
// ---------------------------------------------------------------------------
#[derive(Parser)]
#[command(name = "hello_gui", version, about = "Hello, world! — with a CLI and a GUI.")]
struct Cli {
    /// Optional initial text shown in the GUI window (used when no subcommand is given).
    #[arg(short = 'm', long = "message")]
    message: Option<String>,

    #[command(subcommand)]
    command: Option<Command>,
}

#[derive(Subcommand)]
enum Command {
    /// Print the greeting in the terminal instead of opening a window.
    Cli {
        /// Additional text to append to "Hello, world!" (optional).
        extra: Vec<String>,

        /// Alternative way to pass the additional text.
        #[arg(short = 'm', long = "message")]
        message: Option<String>,
    },
}

// ---------------------------------------------------------------------------
// GUI: egui app. State lives in the struct.
// ---------------------------------------------------------------------------
struct HelloApp {
    /// The text field where the user types additional text.
    extra: String,
}

impl eframe::App for HelloApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            // The greeting comes from the same core::greeting() the CLI uses.
            ui.heading(core::greeting(Some(&self.extra)));
            ui.label("This window was built with Rust and egui — same core as the CLI.");

            ui.add_space(12.0);
            ui.horizontal(|ui| {
                ui.label("Additional text:");
                ui.add_sized([220.0, 22.0], egui::TextEdit::singleline(&mut self.extra));
                if ui.button("Clear").clicked() {
                    self.extra.clear();
                }
            });
        });
    }
}

fn run_gui(initial_extra: Option<String>) -> eframe::Result {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([420.0, 240.0])
            .with_title("Hello from Rust"),
        ..Default::default()
    };
    eframe::run_native(
        "Hello from Rust",
        options,
        Box::new(move |_cc| {
            Ok(Box::new(HelloApp {
                extra: initial_extra.unwrap_or_default(),
            }))
        }),
    )
}

fn main() -> eframe::Result {
    let cli = Cli::parse();

    match cli.command {
        // `hello_gui cli ...` -> terminal path.
        Some(Command::Cli { extra, message }) => {
            // Prefer --message; otherwise join all positional words into one line.
            let extra = message
                .filter(|s| !s.trim().is_empty())
                .or_else(|| {
                    let joined = extra.join(" ");
                    (!joined.trim().is_empty()).then_some(joined)
                });
            println!("{}", core::greeting(extra.as_deref()));
            Ok(())
        }
        // No subcommand -> GUI path (double-clickable .app also lands here).
        None => run_gui(cli.message),
    }
}
