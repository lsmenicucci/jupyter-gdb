program teste
    implicit none
    real :: x, y(10, 20, 2) = 0

    y(:, 1, 1) = 1
    print *, x
    y(:, 1, 2) = 2

end program teste
