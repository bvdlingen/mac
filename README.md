# hello_gui — one binary, two faces (macOS, Apple Silicon)

A tiny demo of the pattern you asked about: **one codebase, shared logic, both a
terminal interface and a graphical window.** Built with Rust + egui/eframe.

## The idea

```
src/main.rs
├── mod core        <- the shared logic (greeting()) — no UI code
├── CLI path        <- clap argument parsing  -> calls core::greeting()
└── GUI path        <- egui window            -> calls core::greeting()
```

There is exactly **one** place where the greeting text is built. Adding a
feature means changing `core`, and both interfaces get it for free.

## Use the CLI

```bash
./target/release/hello_gui cli                          # Hello, world!
./target/release/hello_gui cli from the terminal        # Hello, world! from the terminal
./target/release/hello_gui cli "extra text here"        # words joined into one line
./target/release/hello_gui cli -m "via the flag"        # flag form
```

## Use the GUI

```bash
./target/release/hello_gui                              # plain window
./target/release/hello_gui -m "preset text"             # window opens with text filled in
open "../Hello World.app"                               # double-clickable app
open "../Hello World.app" --args -m "preset text"        # app bundle + preset text
```

In the window there is an **Additional text** field — typing in it updates the
greeting live, which is the GUI equivalent of the CLI argument.

## Build

```bash
cargo build --release          # binary at target/release/hello_gui
./make_app.sh                  # packages "Workspace/Hello World.app" (ad-hoc signed)
```

## Growing this into a real app

1. Move `mod core` into its own module or crate as it grows (`src/core/`, or a
   workspace member) and keep it free of any egui/clap types.
2. Keep the two thin front-ends dumb: they only translate input (arguments,
   widgets) into calls on `core`, and render what `core` returns.
3. Anything that needs to run headless — cron, scripts, CI — uses the `cli`
   path; a human uses the window. Same rules, same output.
