program parallel
    use mpi
    implicit none
    integer :: size, rank, ierr 
    integer process_Rank, size_Of_Cluster, ierror
    integer, parameter :: n = 10
    real :: x(n)
    integer :: i

    ! Initialize MPI
    call MPI_INIT(ierr)

    ! Gather size and rank
    call MPI_COMM_SIZE(MPI_COMM_WORLD, size, ierror)
    call MPI_COMM_RANK(MPI_COMM_WORLD, rank, ierror)

    ! Do some rank-dependent computation
    do i = 1, n
        x(i) = i + REAL(rank)/REAL(size)  
    end do

    if (rank == 0) then
        x = -x
    end if

    ! Sync all ranks
    call MPI_BARRIER(MPI_COMM_WORLD, ierror)

    print *, rank, x
    
    ! Finalize MPI, no communication is expected after this
    call MPI_FINALIZE(ierr)
end program
