# Desktop plugin lives in its own repository

The Omarchy plugin (`khephri.worldline`) is developed in `~/Projects/worldline-omarchy` and
deployed as a **git checkout** at `~/.config/omarchy/plugins/khephri.worldline`. This
directory used to hold a copy of the QML; that copy drifted from the real plugin (the 1.0
snapshot here would have overwritten the deployed 1.1 cockpit on the next `./install.sh`),
so it was removed in 1.1.0. `install.sh` now fast-forwards the checkout instead.
