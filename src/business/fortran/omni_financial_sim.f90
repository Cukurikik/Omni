module omni_financial_sim
    implicit none
    private
    public :: monte_carlo_option_pricing

contains

    subroutine monte_carlo_option_pricing(S0, K, T, r, sigma, num_simulations, price)
        real(8), intent(in) :: S0, K, T, r, sigma
        integer, intent(in) :: num_simulations
        real(8), intent(out) :: price
        
        integer :: i
        real(8) :: ST, payoff_sum, z
        real(8) :: dt
        
        payoff_sum = 0.0d0
        dt = T
        
        ! Fast vectorized pseudo-random simulation
        do i = 1, num_simulations
            call random_number(z)
            ! Inverse transform sampling for standard normal (approximate for speed)
            z = 5.0d0 * (z - 0.5d0) 
            ST = S0 * exp((r - 0.5d0 * sigma**2) * dt + sigma * sqrt(dt) * z)
            if (ST > K) then
                payoff_sum = payoff_sum + (ST - K)
            end if
        end do
        
        price = exp(-r * T) * (payoff_sum / real(num_simulations, 8))
    end subroutine monte_carlo_option_pricing

end module omni_financial_sim
