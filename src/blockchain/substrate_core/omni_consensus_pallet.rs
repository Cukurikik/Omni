#![cfg_attr(not(feature = "std"), no_std)]

// Omni Substrate Pallet in Rust
// Core consensus bridging for Omni Blockchain integrations.

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;

    #[pallet::pallet]
    #[pallet::generate_store(pub(super) trait Store)]
    pub struct Pallet<T>(_);

    #[pallet::config]
    pub trait Config: frame_system::Config {}

    #[pallet::error]
    pub enum Error<T> {
        NoneValue,
        StorageOverflow,
    }

    #[pallet::storage]
    #[pallet::getter(fn omni_state)]
    pub type OmniState<T> = StorageValue<_, u32>;

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::weight(10_000)]
        pub fn update_state(origin: OriginFor<T>, new_val: u32) -> DispatchResult {
            ensure_signed(origin)?;
            
            // Deterministic state update with monadic error handling
            let current = OmniState::<T>::get().unwrap_or(0);
            let next = current.checked_add(new_val).ok_or(Error::<T>::StorageOverflow)?;
            
            OmniState::<T>::put(next);
            Ok(())
        }
    }
}
